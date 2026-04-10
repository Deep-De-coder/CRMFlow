from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class OpportunityStage(str, Enum):
    PROSPECTING = "Prospecting"
    QUALIFICATION = "Qualification"
    NEEDS_ANALYSIS = "Needs Analysis"
    VALUE_PROPOSITION = "Value Proposition"
    DECISION_MAKERS = "Id. Decision Makers"
    PERCEPTION_ANALYSIS = "Perception Analysis"
    PROPOSAL = "Proposal/Price Quote"
    NEGOTIATION = "Negotiation/Review"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"


class OpportunityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    stage_name: OpportunityStage
    close_date: str = Field(..., description="Format: YYYY-MM-DD")
    amount: Optional[float] = None
    account_id: Optional[str] = None
    probability: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    lead_source: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    stage_name: Optional[OpportunityStage] = None
    close_date: Optional[str] = None
    amount: Optional[float] = None
    probability: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    lead_source: Optional[str] = None


class OpportunityResponse(OpportunityBase):
    id: str
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None
    is_closed: Optional[bool] = None
    is_won: Optional[bool] = None

    model_config = {"from_attributes": True}
