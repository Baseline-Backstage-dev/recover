from typing import Dict

from pulumi import ComponentResource, ResourceOptions, get_project
from pulumi_aws import dynamodb

from recover.tables import dynamodb_tables


class DynamoDBArgs:
    def __init__(self, table_name: str, key: Dict):
        self.table_name = table_name
        self.key = key


class DynamoDBTable(ComponentResource):
    """
    Class for building AWS Lambda Functions
    """

    def __init__(self, name: str, args: DynamoDBArgs, opts: ResourceOptions = None):
        super().__init__(t=f"sai:{get_project()}:DynamoDB", name=name, props={}, opts=opts)
        dynamodb.Table(
            resource_name=args.table_name,
            name=args.table_name,
            attributes=[
                dynamodb.TableAttributeArgs(
                    name=args.key["hash_key"]["name"],
                    type=args.key["hash_key"]["type"],
                ),
            ],
            hash_key=args.key["hash_key"]["name"],
            billing_mode="PAY_PER_REQUEST",
            table_class="STANDARD_INFREQUENT_ACCESS",
            opts=ResourceOptions(parent=self),
        )


class DynamoDBFactory:
    @staticmethod
    def build():
        for table_name, key in dynamodb_tables.items():
            DynamoDBTable(table_name, DynamoDBArgs(table_name=table_name, key=key))
