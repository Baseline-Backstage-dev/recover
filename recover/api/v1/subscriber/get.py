import json
import logging
from typing import Any

from openapi_schema_pydantic.util import PydanticSchema

from recover.domain.subscriber.crud import SubscriberCrud
from recover.domain.subscriber.models import SubscriberModel

logger = logging.getLogger(__name__)

schema = {
    "parameters": [
        {
            "in": "query",
            "required": True,
            "type": "str",
            "name": "id",
            "description": "subscriber id to fetch",
        }
    ],
    "responses": {
        "200": {
            "description": "Information on a subscriber",
            "content": {"application/json": {"schema": PydanticSchema(schema_class=SubscriberModel)}},
        },
        "404": {"description": "No subscriber found with the provided id"},
    },
}


def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    subscriber_id = event["queryStringParameters"]["id"]
    subscriber = SubscriberCrud.read(subscriber_id)

    if not subscriber:
        return {
            "statusCode": 404,
            "body": "No subscriber found with the provided id",
        }

    return {
        "statusCode": 200,
        "body": json.dumps(subscriber),
    }
