from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.contact import (
    ContactCreate, ContactUpdate, ContactResponse
)
from app.services.contact_service import ContactService
from app.salesforce.client import get_sf_client
from app.salesforce.exceptions import (
    RecordNotFoundError, SalesforceServiceError
)
from typing import Optional

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def get_contact_service() -> ContactService:
    return ContactService(get_sf_client())


@router.get("/", response_model=list[ContactResponse])
def list_contacts(
    account_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ContactService = Depends(get_contact_service),
):
    try:
        return service.list_contacts(
            account_id=account_id, limit=limit, offset=offset
        )
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service),
):
    try:
        return service.get_contact(contact_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(
    data: ContactCreate,
    service: ContactService = Depends(get_contact_service),
):
    try:
        return service.create_contact(data)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    data: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
):
    try:
        return service.update_contact(contact_id, data)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: str,
    service: ContactService = Depends(get_contact_service),
):
    try:
        service.delete_contact(contact_id)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except SalesforceServiceError as e:
        raise HTTPException(status_code=500, detail=e.message)
