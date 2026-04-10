from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.account import (
    AccountCreate, AccountUpdate, AccountResponse
)
from app.services.account_service import AccountService
from app.salesforce.client import get_sf_client
from app.salesforce.exceptions import (
    RecordNotFoundError, SalesforceServiceError
)
from typing import Optional

router = APIRouter(prefix="/accounts", tags=["Accounts"])


def get_account_service() -> AccountService:
    return AccountService(get_sf_client())


@router.get("/", response_model=list[AccountResponse])
def list_accounts(
    industry: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.list_accounts(
            industry=industry, limit=limit, offset=offset
        )
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/search", response_model=list[AccountResponse])
def search_accounts(
    name: str = Query(..., min_length=1),
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.search_accounts(name)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.get_account(account_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(
    data: AccountCreate,
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.create_account(data)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: str,
    data: AccountUpdate,
    service: AccountService = Depends(get_account_service),
):
    try:
        return service.update_account(account_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{account_id}", status_code=204)
def delete_account(
    account_id: str,
    service: AccountService = Depends(get_account_service),
):
    try:
        service.delete_account(account_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)
