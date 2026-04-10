from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.opportunity import (
    OpportunityCreate, OpportunityUpdate,
    OpportunityResponse, OpportunityStage
)
from app.services.opportunity_service import OpportunityService
from app.salesforce.client import get_sf_client
from app.salesforce.exceptions import (
    RecordNotFoundError, SalesforceServiceError
)
from typing import Optional

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def get_opportunity_service() -> OpportunityService:
    return OpportunityService(get_sf_client())


@router.get("/", response_model=list[OpportunityResponse])
def list_opportunities(
    stage: Optional[OpportunityStage] = Query(None),
    account_id: Optional[str] = Query(None),
    is_closed: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        return service.list_opportunities(
            stage=stage, account_id=account_id,
            is_closed=is_closed, limit=limit, offset=offset,
        )
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/pipeline", response_model=dict)
def get_pipeline_summary(
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        return service.get_pipeline_summary()
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{opp_id}", response_model=OpportunityResponse)
def get_opportunity(
    opp_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        return service.get_opportunity(opp_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=OpportunityResponse, status_code=201)
def create_opportunity(
    data: OpportunityCreate,
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        return service.create_opportunity(data)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.patch("/{opp_id}", response_model=OpportunityResponse)
def update_opportunity(
    opp_id: str,
    data: OpportunityUpdate,
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        return service.update_opportunity(opp_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{opp_id}", status_code=204)
def delete_opportunity(
    opp_id: str,
    service: OpportunityService = Depends(get_opportunity_service),
):
    try:
        service.delete_opportunity(opp_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)
