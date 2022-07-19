import json
from importlib import reload

import pytest
from moto import mock_dynamodb

from recover.api.v1.subscriber import post
from recover.domain.subscriber import crud
from tests.test_util.tables import create_mock_subscriber_table


@mock_dynamodb
class TestSubscriberCrud:
    def setup_method(self, method):
        create_mock_subscriber_table()

        reload(crud)  # Reload within the mock
        reload(post)  # Reload within the mock

    @pytest.mark.usefixtures("post_subscriber_event")
    def test_good_subscriber(self, post_subscriber_event):
        # Do a post request with a good subscriber body
        response = post.handler(post_subscriber_event, {})

        # Check the status code
        assert response["statusCode"] == 201, f"{response['statusCode']} != 201, body: {response['body']}"

        # Check that all expected keys (including automatically generated) are in the object that's inserted
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

    @pytest.mark.usefixtures("post_subscriber_event")
    def test_bad_subscriber(self, subscriber_in):
        # Pop a key to make it fail validation
        subscriber_in.pop("company_name")
        event = {
            "body": json.dumps({"subscriber": subscriber_in}),
            "isBase64Encoded": False,
        }

        # Do a post request with a good subscriber body
        response = post.handler(event, {})

        # Check the bad request status code
        assert response["statusCode"] == 400, f"{response['statusCode']} != 201, body: {response['body']}"
