from pydantic import BaseModel, Field
from typing import Optional


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None
    number_of_employees: Optional[int] = None
    annual_revenue: Optional[float] = None
    description: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None
    number_of_employees: Optional[int] = None
    annual_revenue: Optional[float] = None
    description: Optional[str] = None


class AccountResponse(AccountBase):
    id: str
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None

    model_config = {"from_attributes": True}
