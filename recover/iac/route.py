import logging
import os
from pathlib import Path
from runpy import run_path
from typing import Any, Optional, Sequence

import pulumi_aws as aws
import pulumi_aws_apigateway as api
from openapi_schema_pydantic import OpenAPI
from openapi_schema_pydantic.util import construct_open_api_with_schema_class
from pulumi import ComponentResource, Output, ResourceOptions, get_stack
from pulumi_aws.iam import RolePolicy

from recover.const import ACCEPTED_API_METHODS, API_AUTHORIZATION_HEADER
from recover.iac._lambda import Lambda, LambdaArgs

logger = logging.getLogger(__name__)


class RouteFactory:
    @staticmethod
    def _get_endpoint(path: Path, lambda_resource_path: Path) -> str:
        """
        extracts the endpoint name from relational parental path:
        example:
            for given path = ../../src/sl/products/delivery/post.py
            the endpoint is: /products/delivery
            this endpoint is used to call the api using
            specified method in the handler python file(i.e. POST method for post.py)
        """
        endpoint = str(path.parent).replace(str(lambda_resource_path), "")
        return endpoint if endpoint[0] == "/" else ("/" + endpoint)

    @staticmethod
    def _get_request_params(path: Path):
        validation = run_path(str(path))
        request_params = validation.get("request_params")

        if not request_params:
            return []

        return [api.RequiredParameterArgs(**params) for params in request_params]

    @staticmethod
    def _get_authorizers(cognito_user_pool_arn) -> Optional[Sequence[api.AuthorizerArgs]]:
        authorizers = []
        if get_stack() != "localstack":
            if cognito_user_pool_arn is not None:
                authorizers.append(
                    api.AuthorizerArgs(
                        parameter_name="Authorization",
                        identity_source=[API_AUTHORIZATION_HEADER],
                        provider_arns=[cognito_user_pool_arn],
                    )
                )
        return authorizers

    @staticmethod
    def _get_base_docs(app_name: str, app_version: str, api_url: str) -> dict[str, Any]:
        return {
            "info": {"title": f"{app_name} API", "version": app_version},
            "servers": [{"description": "base url", "url": api_url}],
            "paths": {},
        }

    @staticmethod
    def _add_schema(docs_dict: dict[str, Any], rest_method: str, endpoint: str, path: Path) -> None:
        """Adds the schema found in the method file to the openapi specs."""
        validation = run_path(str(path))
        schema = validation.get("schema")

        if schema is None:
            raise Exception(
                f"schema is missing in {path}. "
                f"Every API method requires a schema for validation and documentation, please add one."
            )

        if schema == "ignore":
            return

        if endpoint in docs_dict["paths"]:
            docs_dict["paths"][endpoint][rest_method] = schema
        else:
            docs_dict["paths"][endpoint] = {rest_method: schema}

    @staticmethod
    def _generate_openapi(docs_dict: dict[str, Any], lambda_resource_path: Path) -> None:
        open_api = construct_open_api_with_schema_class(OpenAPI.parse_obj(docs_dict))

        # Write the resulting openapi specs to a standard location within the api
        openapi_file_path = lambda_resource_path.joinpath("docs/openapi.json")
        openapi_file_path.unlink(missing_ok=True)
        with open(openapi_file_path, "w") as f:
            f.write(open_api.json(by_alias=True, exclude_none=True, indent=2))

    @staticmethod
    def build(
        app_name: str,
        app_version: str,
        base_api_path: Path,
        lambda_resource_path: Path,
        default_role_arn: Output[str],
        default_policy: RolePolicy,
        cognito_user_pool_arn: Output[str],
        default_lambda_layers: Optional[list[aws.lambda_.LayerVersion]] = None,
        parent_api: Optional[ComponentResource] = None,
    ):
        docs_dict = RouteFactory._get_base_docs(app_name=app_name, app_version=app_version, api_url=str(base_api_path))

        routes = []
        for current_path, folders, files in os.walk(lambda_resource_path):
            """
            For example:
            file:  get.py
            lambda_resource_path:  /source/api/v1
            rest_method:  get
            endpoint:  /subscriber
            """
            for file in files:
                path = Path(os.path.join(current_path, file))

                rest_method = path.stem
                if rest_method not in ACCEPTED_API_METHODS:
                    continue
                endpoint = RouteFactory._get_endpoint(path=path, lambda_resource_path=lambda_resource_path)

                resource_name = f"{app_name}-lambda{'-'.join(endpoint.split('/'))}-{rest_method}"
                event_handler = Lambda(
                    resource_name,
                    args=LambdaArgs(
                        method=rest_method,
                        endpoint=endpoint,
                        func_dir=f"{lambda_resource_path}{endpoint}",
                        func_handler=f"{rest_method}.handler",
                        func_name=resource_name,
                        default_role_arn=default_role_arn,
                        default_lambda_layers=default_lambda_layers,
                    ),
                    opts=ResourceOptions(parent=parent_api, depends_on=[default_policy]),
                ).lambda_function

                routes.append(
                    api.RouteArgs(
                        path=f"{base_api_path}{endpoint}",
                        method=api.Method(rest_method.upper()),
                        event_handler=event_handler,
                        # Define a request authorizer which uses Lambda or cognito user pool to validate the token
                        # from the Authorization header
                        authorizers=RouteFactory._get_authorizers(cognito_user_pool_arn),
                        api_key_required=False,
                    )
                )

                # Add the endpoint schema to the openapi docs
                RouteFactory._add_schema(docs_dict=docs_dict, rest_method=rest_method, endpoint=endpoint, path=path)

        # Finally generate the openapi specs and add local static files to the routes
        RouteFactory._generate_openapi(docs_dict=docs_dict, lambda_resource_path=lambda_resource_path)
        routes.append(api.RouteArgs(path="/", local_path=str(lambda_resource_path / "docs")))

        return routes
