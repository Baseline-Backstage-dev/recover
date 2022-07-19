import boto3

from recover.tables import dynamodb_tables, subscriber_table_name


def create_mock_subscriber_table():
    dynamodb = boto3.resource("dynamodb")
    table_config = dynamodb_tables[subscriber_table_name]

    return dynamodb.create_table(
        TableName=subscriber_table_name,
        KeySchema=[
            {"AttributeName": table_config["hash_key"]["name"], "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": table_config["hash_key"]["name"], "AttributeType": table_config["hash_key"]["type"]},
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )
