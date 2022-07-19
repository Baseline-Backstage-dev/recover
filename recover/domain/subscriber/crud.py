import logging
from typing import Any, Optional

import boto3

from recover.tables import subscriber_table_name

logger = logging.getLogger(__name__)


class SubscriberCrud:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(subscriber_table_name)

    @classmethod
    def create(cls, subscriber: dict[str, Any]) -> dict[str, Any]:
        logger.info("creating subscriber")

        cls.table.put_item(Item=subscriber)

        return subscriber

    @classmethod
    def read(cls, subscriber_id: str) -> Optional[dict[str, Any]]:
        logger.info("reading subscriber")

        db_response = cls.table.get_item(Key={"id": subscriber_id})

        return db_response.get("Item")

    @classmethod
    def delete(cls, subscriber_id: str) -> str:
        logger.info("delete subscriber")

        db_response = cls.table.delete_item(Key={"id": subscriber_id})

        if db_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            message = f"Item with id {subscriber_id} successfully deleted"
        else:
            message = f"Item with id {subscriber_id} was not found"

        return message


class SubscriberListCrud:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(subscriber_table_name)

    @classmethod
    def read(cls, subscriber_ids: Optional[str]) -> dict[str, Any]:
        logger.info("reading subscribers")

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(subscriber_table_name)

        if subscriber_ids:
            db_response = dynamodb.batch_get_item(
                RequestItems={subscriber_table_name: {"Keys": [{"id": sub_id} for sub_id in subscriber_ids]}}
            )
            items = db_response["Responses"][subscriber_table_name]

            # Dynamo's batch_get_item response has a limit of 16 MB
            # UnprocessedKeys indicates the keys that haven't been fetched yet
            while db_response.get("UnprocessedKeys"):
                db_response = dynamodb.batch_get_item(RequestItems=db_response["UnprocessedKeys"])
                items.extend(db_response["Responses"][subscriber_table_name])
        else:
            db_response = table.scan()
            items = db_response["Items"]

            # Dynamo's scan response has a limit of 1 MB
            # LastEvaluatedKey indicates that there are more results
            while "LastEvaluatedKey" in db_response:
                db_response = table.query(ExclusiveStartKey=db_response["LastEvaluatedKey"])
                items.update(db_response["Items"])

        return items
