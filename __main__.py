import os
from pathlib import Path

import pulumi
import pulumi_aws as aws

from recover.infra import build_infra, register_auto_tags

# General config
app_name = "recover"
app_version = "0.0.1"
current_region = aws.get_region()
auth_callback_urls = ["https://example.com"]

# Pulumi config
config = pulumi.Config()
stage = config.require("stage")

# Register tag in all AWS resources, useful to control costs and environments
register_auto_tags(
    {
        "user:Project": pulumi.get_project(),
        "user:Stack": pulumi.get_stack(),
    }
)

# API config
base_api_path = Path("/api/v1")

# Zip file for the lambda layer
current_path = Path(os.path.dirname(os.path.realpath(__file__)))
lambda_layer_path = current_path.joinpath("lambda_layer/lambda_layer.zip")
lambda_resource_path = current_path.joinpath("recover/api/v1/")


if pulumi.get_stack() == "localstack":
    config_aws = pulumi.Config("aws")
    localstack = aws.Provider(
        "localstack",
        aws.ProviderArgs(
            region="eu-west-1",
            endpoints=[
                aws.ProviderEndpointArgs(
                    acm="http://localhost:4566",
                    amplify="http://localhost:4566",
                    apigateway="http://localhost:4566",
                    apigatewayv2="http://localhost:4566",
                    applicationautoscaling="http://localhost:4566",
                    appsync="http://localhost:4566",
                    athena="http://localhost:4566",
                    autoscaling="http://localhost:4566",
                    batch="http://localhost:4566",
                    cloudformation="http://localhost:4566",
                    cloudfront="http://localhost:4566",
                    cloudsearch="http://localhost:4566",
                    cloudtrail="http://localhost:4566",
                    cloudwatch="http://localhost:4566",
                    cloudwatchevents="http://localhost:4566",
                    cloudwatchlogs="http://localhost:4566",
                    codecommit="http://localhost:4566",
                    cognitoidentity="http://localhost:4566",
                    cognitoidp="http://localhost:4566",
                    docdb="http://localhost:4566",
                    dynamodb="http://localhost:4566",
                    ec2="http://localhost:4566",
                    ecr="http://localhost:4566",
                    ecs="http://localhost:4566",
                    eks="http://localhost:4566",
                    elasticache="http://localhost:4566",
                    elasticbeanstalk="http://localhost:4566",
                    elb="http://localhost:4566",
                    emr="http://localhost:4566",
                    es="http://localhost:4566",
                    firehose="http://localhost:4566",
                    glacier="http://localhost:4566",
                    glue="http://localhost:4566",
                    iam="http://localhost:4566",
                    iot="http://localhost:4566",
                    kafka="http://localhost:4566",
                    kinesis="http://localhost:4566",
                    kinesisanalytics="http://localhost:4566",
                    kms="http://localhost:4566",
                    lambda_="http://localhost:4566",
                    mediastore="http://localhost:4566",
                    neptune="http://localhost:4566",
                    organizations="http://localhost:4566",
                    qldb="http://localhost:4566",
                    rds="http://localhost:4566",
                    redshift="http://localhost:4566",
                    route53="http://localhost:4566",
                    s3="http://localhost:4566",
                    sagemaker="http://localhost:4566",
                    secretsmanager="http://localhost:4566",
                    servicediscovery="http://localhost:4566",
                    ses="http://localhost:4566",
                    sns="http://localhost:4566",
                    sqs="http://localhost:4566",
                    ssm="http://localhost:4566",
                    stepfunctions="http://localhost:4566",
                    sts="http://localhost:4566",
                    swf="http://localhost:4566",
                    transfer="http://localhost:4566",
                    xray="http://localhost:4566",
                )
            ],
            access_key="test",
            secret_key="test",
            s3_use_path_style=True,
            # s3_force_path_style=True,
            skip_credentials_validation=True,
            skip_requesting_account_id=True,
            skip_metadata_api_check=True,
            skip_region_validation=True,
            skip_get_ec2_platforms=True,
        ),
    )

    build_infra(
        app_name=app_name,
        app_version=app_version,
        stage=stage,
        base_api_path=base_api_path,
        lambda_resource_path=lambda_resource_path,
        lambda_layer_path=lambda_layer_path,
        custom_provider=localstack,
        auth_callback_urls=auth_callback_urls,
    )
else:
    build_infra(
        app_name=app_name,
        app_version=app_version,
        stage=stage,
        base_api_path=base_api_path,
        lambda_resource_path=lambda_resource_path,
        lambda_layer_path=lambda_layer_path,
        auth_callback_urls=auth_callback_urls,
    )
