from app.services.base import BaseService
from app.models.contact import (
    ContactCreate, ContactUpdate, ContactResponse
)
from typing import Optional

CONTACT_FIELDS = [
    "Id", "FirstName", "LastName", "Email", "Phone",
    "Title", "Department", "AccountId",
    "CreatedDate", "LastModifiedDate",
]


class ContactService(BaseService):
    """
    Service layer for Salesforce Contact operations.
    Supports filtering by account and email search.
    """

    sf_object = "Contact"

    def list_contacts(
        self,
        account_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ContactResponse]:
        where = None
        if account_id:
            where = f"AccountId = '{account_id}'"
        soql = self._build_soql(CONTACT_FIELDS, where=where,
                                limit=limit, offset=offset)
        records = self._execute_query(soql)
        return [self._to_response(r) for r in records]

    def get_contact(self, contact_id: str) -> ContactResponse:
        record = self._get_by_id(contact_id)
        return self._to_response(record)

    def create_contact(self, data: ContactCreate) -> ContactResponse:
        payload = self._to_sf_payload(data.model_dump(exclude_none=True))
        new_id = self._create(payload)
        return self.get_contact(new_id)

    def update_contact(
        self, contact_id: str, data: ContactUpdate
    ) -> ContactResponse:
        payload = self._to_sf_payload(
            data.model_dump(exclude_none=True)
        )
        self._update(contact_id, payload)
        return self.get_contact(contact_id)

    def delete_contact(self, contact_id: str) -> bool:
        return self._delete(contact_id)

    @staticmethod
    def _to_sf_payload(data: dict) -> dict:
        mapping = {
            "first_name": "FirstName",
            "last_name": "LastName",
            "email": "Email",
            "phone": "Phone",
            "title": "Title",
            "department": "Department",
            "account_id": "AccountId",
        }
        return {
            mapping[k]: v
            for k, v in data.items()
            if k in mapping and v is not None
        }

    @staticmethod
    def _to_response(record: dict) -> ContactResponse:
        return ContactResponse(
            id=record.get("Id", ""),
            first_name=record.get("FirstName"),
            last_name=record.get("LastName", ""),
            email=record.get("Email"),
            phone=record.get("Phone"),
            title=record.get("Title"),
            department=record.get("Department"),
            account_id=record.get("AccountId"),
            created_date=str(record.get("CreatedDate", "")),
            last_modified_date=str(record.get("LastModifiedDate", "")),
        )
