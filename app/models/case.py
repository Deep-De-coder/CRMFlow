from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CaseStatus(str, Enum):
    NEW = "New"
    WORKING = "Working"
    ESCALATED = "Escalated"
    CLOSED = "Closed"


class CasePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class CaseBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    status: CaseStatus = CaseStatus.NEW
    priority: CasePriority = CasePriority.MEDIUM
    description: Optional[str] = None
    account_id: Optional[str] = None
    contact_id: Optional[str] = None
    origin: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    description: Optional[str] = None
    origin: Optional[str] = None


class CaseResponse(CaseBase):
    id: str
    case_number: Optional[str] = None
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None
    is_closed: Optional[bool] = None

    model_config = {"from_attributes": True}
