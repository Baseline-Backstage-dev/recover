import json

from pulumi import ComponentResource, ResourceOptions, get_project
from pulumi_aws.iam import Role, RolePolicy


class LambdaIAM(ComponentResource):
    def __init__(self, app_name, opts: ResourceOptions = None):
        """
        Class for create all IAM resources used by application
        """
        super().__init__(t=f"sai:{get_project()}:IAM", name=app_name, props={}, opts=opts)
        role_name = f"{app_name}-lambda-invocation-role"

        self.lambda_role = Role(
            role_name,
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
            opts=ResourceOptions(parent=self),
        )
        self.lambda_role_policy = RolePolicy(
            f"{app_name}-lambda-invocation-policy",
            role=self.lambda_role.id,
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "Stmt1428341300017",
                            "Action": [
                                "dynamodb:DeleteItem",
                                "dynamodb:GetItem",
                                "dynamodb:PutItem",
                                "dynamodb:Query",
                                "dynamodb:Scan",
                                "dynamodb:UpdateItem",
                            ],
                            "Effect": "Allow",
                            "Resource": "*",
                        },
                        {
                            "Sid": "",
                            "Resource": "*",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Effect": "Allow",
                        },
                    ],
                },
            ),
            opts=ResourceOptions(parent=self),
        )
