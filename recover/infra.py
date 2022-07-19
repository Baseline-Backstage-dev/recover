from pathlib import Path
from typing import Optional, Sequence

import pulumi

from recover.const import aws_is_taggable
from recover.iac.api_gateway import APIGateway, APIGatewayArgs
from recover.iac.dynamodb import DynamoDBFactory


def build_infra(
    app_name: str,
    app_version: str,
    stage: str,
    base_api_path: Path,
    lambda_resource_path: Path,
    lambda_layer_path: Optional[Path] = None,
    custom_provider: pulumi.ProviderResource = None,
    auth_callback_urls: Optional[Sequence[str]] = None,
):
    # DynamoDB - WIP
    DynamoDBFactory.build()

    # API
    APIGateway(
        app_name=app_name,
        app_version=app_version,
        args=APIGatewayArgs(
            stage=stage,
            base_api_path=base_api_path,
            lambda_resource_path=lambda_resource_path,
            custom_provider=custom_provider,
            lambda_layer_path=lambda_layer_path,
            auth_callback_urls=auth_callback_urls,
        ),
    )


# registerAutoTags registers a global stack transformation that merges a set
# of tags with whatever was also explicitly added to the resource definition.
def register_auto_tags(auto_tags):
    pulumi.runtime.register_stack_transformation(lambda args: _auto_tag(args, auto_tags))


# auto_tag applies the given tags to the resource properties if applicable.
def _auto_tag(args, auto_tags):
    if aws_is_taggable(args.type_):
        args.props["tags"] = {**(args.props["tags"] or {}), **auto_tags}
        return pulumi.ResourceTransformationResult(args.props, args.opts)
