from typing import Optional, Sequence

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions, get_project


class CognitoArgs:
    def __init__(
        self,
        user_pool_name: str,
        auth_flows: Optional[Sequence[str]] = None,
        allowed_oauth_flows: Optional[Sequence[str]] = None,
        allowed_oauth_scopes: Optional[Sequence[str]] = None,
        auth_callback_urls: Optional[Sequence[str]] = None,
    ):
        if allowed_oauth_scopes is None:
            allowed_oauth_scopes = [
                "email",
                "openid",
                "aws.cognito.signin.user.admin",
                "profile",
            ]
        if allowed_oauth_flows is None:
            allowed_oauth_flows = ["code", "implicit"]
        if auth_flows is None:
            auth_flows = [
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ]

        self.user_pool_name = user_pool_name
        self.auth_flows = auth_flows
        self.allowed_oauth_flows = allowed_oauth_flows
        self.allowed_oauth_scopes = allowed_oauth_scopes
        self.auth_callback_urls = auth_callback_urls


class Cognito(ComponentResource):
    """
    Class for building Cognito User Pool and all of its necessary components
    """

    def __init__(self, name: str, args: CognitoArgs, opts: ResourceOptions = None):
        super().__init__(t=f"sai:{get_project()}:Cognito", name=name, props={}, opts=opts)
        self.name = name
        self.args = args
        user_pool_name = f"{name}-user-pool"
        self.user_pool = aws.cognito.UserPool(
            resource_name=user_pool_name,
            name=user_pool_name,
            opts=ResourceOptions(parent=self),
        )
        self.add_user_pool_domain(name)
        user_pool_client = self.add_user_pool_client()

        self.register_outputs(
            {
                "cognito-user-pool-endpoint": self.user_pool.endpoint,
                "cognito-user-pool-id": self.user_pool.id,
                "cognito-api-client-id": user_pool_client.id,
                "cognito-api-client-secret": user_pool_client.client_secret,
            }
        )

        pulumi.export("cognito-user-pool-endpoint", self.user_pool.endpoint)
        pulumi.export("cognito-application-endpoint", user_pool_client.callback_urls)
        pulumi.export("cognito-user-pool-id", self.user_pool.id)
        pulumi.export("cognito-api-client-id", user_pool_client.id)
        pulumi.export("cognito-api-client-secret", user_pool_client.client_secret)

    def add_user_pool_client(self):
        user_pool_client_name = f"{self.name}-user-pool-client"
        user_pool_client = aws.cognito.UserPoolClient(
            user_pool_client_name,
            user_pool_id=self.user_pool.id,
            allowed_oauth_flows_user_pool_client=True,
            callback_urls=self.args.auth_callback_urls,
            logout_urls=[callback + "/logout" for callback in self.args.auth_callback_urls],
            supported_identity_providers=["COGNITO"],
            allowed_oauth_flows=self.args.allowed_oauth_flows,
            allowed_oauth_scopes=self.args.allowed_oauth_scopes,
            opts=ResourceOptions(parent=self),
        )
        return user_pool_client

    def add_user_pool_domain(self, name: str):
        user_pool_domain_name = f"{name}-user-pool-domain"
        user_pool_domain = aws.cognito.UserPoolDomain(
            user_pool_domain_name,
            domain=f"{get_project()}-sai",
            user_pool_id=self.user_pool.id,
            opts=ResourceOptions(parent=self),
        )
        return user_pool_domain
