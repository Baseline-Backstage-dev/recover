import json

import pytest

from recover.domain.subscriber.models import OnboardingStatus


@pytest.fixture
def subscriber_in():
    return {
        "company_name": "Legal Firm",
        "coc_registration_number": "xy123",
        "coc_registration_name": "Legal Firm B.V.",
        "email": "ceo@legalfirm.com",
        "username": "mrbigshot",
    }


@pytest.fixture
def subscriber_in2():
    return {
        "company_name": "Legal Firm 2",
        "coc_registration_number": "yz456",
        "coc_registration_name": "Legal Firm 2 B.V.",
        "email": "ceo@legalfirm2.com",
        "username": "mrsbigshot",
    }


@pytest.fixture
def post_subscriber_event(subscriber_in):
    return {
        "body": json.dumps({"subscriber": subscriber_in}),
        "isBase64Encoded": False,
    }


@pytest.fixture
def post_subscriber_event2(subscriber_in2):
    return {
        "body": json.dumps({"subscriber": subscriber_in2}),
        "isBase64Encoded": False,
    }


@pytest.fixture
def subscriber_complete(subscriber_in):
    return {
        **subscriber_in,
        **{
            "id": "22ff7590-1758-4dd7-a70d-4e5d85de3479",
            "subscribed_at": "2000-1-1 00:00:00",
            "approved_at": None,
            "onboarding_status": OnboardingStatus.subscribed,
        },
    }
