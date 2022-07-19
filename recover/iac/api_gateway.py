from pathlib import Path
from typing import Optional, Sequence

import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway
from pulumi import (
    ComponentResource,
    FileArchive,
    Output,
    ProviderResource,
    ResourceOptions,
    export,
    get_project,
    get_stack,
)

from recover.iac.cognito import Cognito, CognitoArgs
from recover.iac.lambda_iam import LambdaIAM
from recover.iac.route import RouteFactory


class APIGatewayArgs:
    """
    Class for building an AWS API Gateway parameters
    """

    def __init__(
        self,
        stage: str,
        base_api_path: Path,
        lambda_resource_path: Path,
        custom_provider: Optional[ProviderResource] = None,
        lambda_layer_path: Optional[Path] = None,
        auth_callback_urls: Optional[Sequence[str]] = None,
    ):
        self.stage = stage
        self.base_api_path = base_api_path
        self.lambda_resource_path = lambda_resource_path
        self.custom_provider = custom_provider
        self.lambda_layer_path = lambda_layer_path
        self.auth_callback_urls = auth_callback_urls


class APIGateway(ComponentResource):
    """
    Class for building an AWS API Gateway and all of its necessary components
    """

    def __init__(
        self,
        app_name: str,
        app_version: str,
        args: APIGatewayArgs,
        opts: ResourceOptions = None,
    ):
        super().__init__(t=f"sai:{get_project()}:APIGateway", name=app_name, props={}, opts=opts)
        self.app_name = app_name
        self.app_version = app_version
        self.args = args
        self.opts = opts

        cognito = Cognito(
            name=self.app_name,
            args=CognitoArgs(
                user_pool_name=self.app_name,
                auth_callback_urls=self.args.auth_callback_urls,
            ),
        )
        iam = LambdaIAM(app_name, opts=ResourceOptions(parent=self))

        routes = RouteFactory.build(
            app_name=self.app_name,
            app_version=app_version,
            base_api_path=self.args.base_api_path,
            lambda_resource_path=self.args.lambda_resource_path,
            default_role_arn=iam.lambda_role.arn,
            default_policy=iam.lambda_role_policy,
            cognito_user_pool_arn=cognito.user_pool.arn,
            default_lambda_layers=self._get_lambda_layer(),
            parent_api=self,
        )

        core_api = apigateway.RestAPI(
            resource_name=f"{self.app_name}-api",
            routes=routes,
            stage_name=self.args.stage,
            opts=ResourceOptions(parent=self, provider=self.args.custom_provider),
        )

        # Create an API key to manage usage
        default_api_key = aws.apigateway.ApiKey(f"{self.app_name}-default-api-key", opts=ResourceOptions(parent=self))

        # Define usage plan for an API stage
        default_usage_plan = aws.apigateway.UsagePlan(
            f"{self.app_name}-default-usage-plan",
            api_stages=[
                aws.apigateway.UsagePlanApiStageArgs(
                    api_id=core_api.api.id,
                    stage=core_api.stage.stage_name,
                ),
            ],
            opts=ResourceOptions(parent=self),
        )
        # Associate the key to the plan
        aws.apigateway.UsagePlanKey(
            f"{self.app_name}-default-usage-plan-key",
            key_id=default_api_key.id,
            key_type="API_KEY",
            usage_plan_id=default_usage_plan.id,
            opts=ResourceOptions(parent=self),
        )

        # Export the API to get the url
        if get_stack() == "localstack":
            url = Output.concat(
                "http://localhost:4566/restapis/",
                core_api.api.id,
                "/local/_user_request_/",
            )
        else:
            url = core_api.url

        export("api-url", url)

    def _get_lambda_layer(self):
        default_lambda_layer = None
        if self.args.lambda_layer_path:
            if not self.args.lambda_layer_path.exists():
                raise ValueError(
                    "Either set the lambda layer path to None in __main__.py "
                    "or generate the lambda layer zip before running."
                )
            default_lambda_layer = [
                aws.lambda_.LayerVersion(
                    "lambdaLayer",
                    compatible_runtimes=["python3.9"],
                    code=FileArchive(path=str(self.args.lambda_layer_path)),
                    layer_name=f"lambda_layer_{self.app_name}",
                    opts=ResourceOptions(parent=self),
                )
            ]
        return default_lambda_layer
