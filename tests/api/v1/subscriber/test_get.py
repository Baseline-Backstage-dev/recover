import json
from importlib import reload

import pytest
from moto import mock_dynamodb

from recover.api.v1.subscriber import get, post
from recover.domain.subscriber import crud
from tests.test_util.tables import create_mock_subscriber_table


@mock_dynamodb
class TestSubscriberCrud:
    def setup_method(self, method):
        create_mock_subscriber_table()

        reload(crud)  # Reload within the mock
        reload(post)  # Reload within the mock
        reload(get)  # Reload within the mock

    @pytest.mark.usefixtures("post_subscriber_event")
    def test_good_request(self, post_subscriber_event):
        # Post request to create a subscriber
        response = post.handler(post_subscriber_event, {})

        # Now perform the get request with the id that was returned by the post request
        response = get.handler(
            event={
                "isBase64Encoded": False,
                "queryStringParameters": {"id": json.loads(response["body"])["id"]},
            },
            context={},
        )

        # Check the status code
        assert response["statusCode"] == 200, f"{response['statusCode']} != 200, body: {response['body']}"

        # Check that all expected keys (including automatically generated) are in the object that's inserted\
        subscriber = json.loads(response["body"])
        assert not (
            set(subscriber)
            ^ {
                "id",
                "company_name",
                "coc_registration_number",
                "coc_registration_name",
                "email",
                "username",
                "id",
                "subscribed_at",
                "approved_at",
                "onboarding_status",
            }
        )

    # def test_missing_id(self):
    #     # Perform a get request without ID
    #     response = get.handler(
    #         event={
    #             "isBase64Encoded": False,
    #             "queryStringParameters": {},
    #         },
    #         context={},
    #     )
    #
    #     # Check that the request fails because of missing query param
    #     assert (
    #         response["statusCode"] == 400
    #     ), f"{response['statusCode']} != 200, body: {response['body']}"
