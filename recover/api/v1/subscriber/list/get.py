import json
import logging
from typing import Any, Optional

from openapi_schema_pydantic.util import PydanticSchema

from recover.domain.subscriber.crud import SubscriberListCrud
from recover.domain.subscriber.models import SubscriberModel, SubscriberRequest

logger = logging.getLogger(__name__)

schema = {
    "parameters": [
        {
            "in": "query",
            "required": False,
            "type": "array",  # TODO: Type is not picked up by the openapi pydantic package
            "items": SubscriberRequest,
            "name": "ids",
            "description": "subscriber ids to fetch",
        }
    ],
    "responses": {
        "200": {
            "description": "Information on a subscriber",
            "content": {"application/json": {"schema": PydanticSchema(schema_class=SubscriberModel)}},
        },
    },
}


def handler(event: dict[str, Optional[Any]], context: dict[str, Any]) -> dict[str, Any]:
    subscriber_ids = (event.get("queryStringParameters") or {}).get("ids", None)
    subscriber = SubscriberListCrud.read(subscriber_ids)

    return {
        "statusCode": 200,
        "body": json.dumps(subscriber),
    }
