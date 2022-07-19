import json
from importlib import reload

import pytest
from moto import mock_dynamodb

from recover.api.v1.subscriber import post
from recover.api.v1.subscriber.list import get
from recover.domain.subscriber import crud
from tests.test_util.tables import create_mock_subscriber_table


@mock_dynamodb
class TestSubscriberCrud:
    def setup_method(self, method):
        create_mock_subscriber_table()

        reload(crud)  # Reload within the mock
        reload(get)  # Reload within the mock
        reload(post)  # Reload within the mock

    @pytest.mark.usefixtures("post_subscriber_event", "post_subscriber_event2")
    def test_all_subscribers(self, post_subscriber_event, post_subscriber_event2):
        # Post requests to create two subscribers
        post.handler(post_subscriber_event, {})
        post.handler(post_subscriber_event2, {})

        # Now perform the get request with the id that was returned by the post request
        response = get.handler(
            event={
                "isBase64Encoded": False,
                "queryStringParameters": {},
            },
            context={},
        )

        # Check the status code
        assert response["statusCode"] == 200, f"{response['statusCode']} != 200, body: {response['body']}"

        # Check that all expected keys (including automatically generated) are in the object that's inserted\
        subscribers = json.loads(response["body"])
        assert len(subscribers) == 2

    @pytest.mark.usefixtures("post_subscriber_event", "post_subscriber_event2")
    def test_selection(self, post_subscriber_event, post_subscriber_event2):
        # Post requests to create two subscribers
        response = post.handler(post_subscriber_event, {})
        post.handler(post_subscriber_event2, {})

        # Now perform the get request with the id that was returned by the post request
        response = get.handler(
            event={
                "isBase64Encoded": False,
                "queryStringParameters": {"ids": [json.loads(response["body"])["id"]]},
            },
            context={},
        )

        # Check the status code
        assert response["statusCode"] == 200, f"{response['statusCode']} != 200, body: {response['body']}"

        # Check that all expected keys (including automatically generated) are in the object that's inserted\
        subscribers = json.loads(response["body"])
        assert len(subscribers) == 1

    # TODO: Add tests for big payloads
