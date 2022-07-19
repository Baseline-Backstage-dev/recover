import base64
import json
import logging
from typing import Any

from openapi_schema_pydantic.util import PydanticSchema
from pydantic import ValidationError

from recover.domain.subscriber.crud import SubscriberCrud
from recover.domain.subscriber.models import SubscriberModel, SubscriberRequest

logger = logging.getLogger(__name__)


schema = {
    "requestBody": {"content": {"application/json": {"schema": PydanticSchema(schema_class=SubscriberRequest)}}},
    "responses": {
        "201": {
            "description": "Subscriber successfully posted",
            "content": {"application/json": {"schema": PydanticSchema(schema_class=SubscriberModel)}},
        },
        "400": {"description": "Bad request"},
    },
}


def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    # API gateway encodes the body
    data = event["body"]
    if event["isBase64Encoded"]:
        data = base64.b64decode(data)
    subscriber = json.loads(data)["subscriber"]

    # Validate the passed subscriber and generate some extra fields
    try:
        subscriber = SubscriberModel(**subscriber).dict()
    except ValidationError as e:
        return {"statusCode": 400, "body": str(e)}

    subscriber = SubscriberCrud.create(subscriber)

    return {
        "statusCode": 201,
        "body": json.dumps(subscriber),
    }
