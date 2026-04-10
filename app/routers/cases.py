from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.case import (
    CaseCreate, CaseUpdate, CaseResponse,
    CaseStatus, CasePriority
)
from app.services.case_service import CaseService
from app.salesforce.client import get_sf_client
from app.salesforce.exceptions import (
    RecordNotFoundError, SalesforceServiceError
)
from typing import Optional

router = APIRouter(prefix="/cases", tags=["Cases"])


def get_case_service() -> CaseService:
    return CaseService(get_sf_client())


@router.get("/", response_model=list[CaseResponse])
def list_cases(
    status: Optional[CaseStatus] = Query(None),
    priority: Optional[CasePriority] = Query(None),
    account_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: CaseService = Depends(get_case_service),
):
    try:
        return service.list_cases(
            status=status, priority=priority,
            account_id=account_id, limit=limit, offset=offset,
        )
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
):
    try:
        return service.get_case(case_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=CaseResponse, status_code=201)
def create_case(
    data: CaseCreate,
    service: CaseService = Depends(get_case_service),
):
    try:
        return service.create_case(data)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: str,
    data: CaseUpdate,
    service: CaseService = Depends(get_case_service),
):
    try:
        return service.update_case(case_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{case_id}", status_code=204)
def delete_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
):
    try:
        service.delete_case(case_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)
