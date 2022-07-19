import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator

from recover.domain.util.validators import is_alnum_or_hyphen_or_space


class OnboardingStatus(str, Enum):
    subscribed = "subscribed"
    approved = "approved"
    denied = "denied"
    onboarded = "onboarded"


class SubscriberRequest(BaseModel):
    company_name: str

    # Chamber of commerce
    coc_registration_number: str
    coc_registration_name: str

    # Main admin info
    email: str
    username: str

    # Validators
    _validate_company_name = validator("company_name", allow_reuse=True)(is_alnum_or_hyphen_or_space)
    _username = validator("username", allow_reuse=True)(is_alnum_or_hyphen_or_space)


class SubscriberModel(SubscriberRequest):
    # Auto-generated
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscribed_at: str = Field(default_factory=lambda: str(datetime.now()))
    onboarding_status: str = OnboardingStatus.subscribed
    approved_at: Optional[str] = None
