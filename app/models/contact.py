from pydantic import BaseModel, Field
from typing import Optional


class ContactBase(BaseModel):
    first_name: Optional[str] = None
    last_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    account_id: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    account_id: Optional[str] = None


class ContactResponse(ContactBase):
    id: str
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None

    model_config = {"from_attributes": True}
