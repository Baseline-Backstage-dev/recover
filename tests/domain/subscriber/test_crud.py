from importlib import reload

import pytest
from moto import mock_dynamodb

from recover.domain.subscriber import crud
from tests.test_util.tables import create_mock_subscriber_table


@mock_dynamodb
class TestSubscriberCrud:
    def setup_method(self, method):
        create_mock_subscriber_table()

        reload(crud)  # Reload within the mock

    @pytest.mark.usefixtures("subscriber_complete")
    def test_create(self, subscriber_complete):
        # Nothing should go wrong during creation
        crud.SubscriberCrud.create(subscriber_complete)
