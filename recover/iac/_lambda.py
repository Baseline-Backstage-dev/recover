import pulumi_aws as aws
from pulumi import (
    AssetArchive,
    ComponentResource,
    FileArchive,
    Output,
    ResourceOptions,
    get_project,
)

from recover.const import LAMBDA_RUNTIME_VERSION


class LambdaArgs:
    def __init__(
        self,
        method: str,
        endpoint: str,
        func_dir: str,
        func_handler: str,
        func_name: str,
        default_role_arn: Output[str],
        default_lambda_layers,
    ):
        self.method = method
        self.endpoint = endpoint
        self.func_dir = func_dir
        self.func_handler = func_handler
        self.func_name = func_name
        self.default_role_arn = default_role_arn
        self.default_lambda_layers = default_lambda_layers


class Lambda(ComponentResource):
    """
    Class for building AWS Lambda Functions
    """

    def __init__(self, name: str, args: LambdaArgs, opts: ResourceOptions = None):
        super().__init__(t=f"sai:{get_project()}:Lambda", name=name, props={}, opts=opts)
        self.opts = opts
        self.lambda_function = aws.lambda_.Function(
            name,
            name=args.func_name,
            runtime=LAMBDA_RUNTIME_VERSION,
            code=AssetArchive(
                {
                    ".": FileArchive(args.func_dir),
                }
            ),
            timeout=300,
            handler=args.func_handler,
            role=args.default_role_arn,
            layers=args.default_lambda_layers,
            opts=self.opts,
        )
