from app.services.base import BaseService
from app.models.case import (
    CaseCreate, CaseUpdate, CaseResponse,
    CaseStatus, CasePriority
)
from typing import Optional

CASE_FIELDS = [
    "Id", "CaseNumber", "Subject", "Status", "Priority",
    "Description", "AccountId", "ContactId", "Origin",
    "IsClosed", "CreatedDate", "LastModifiedDate",
]


class CaseService(BaseService):
    """
    Service layer for Salesforce Case operations.
    Supports filtering by status, priority, and account.
    """

    sf_object = "Case"

    def list_cases(
        self,
        status: Optional[CaseStatus] = None,
        priority: Optional[CasePriority] = None,
        account_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[CaseResponse]:
        conditions = []
        if status:
            conditions.append(f"Status = '{status.value}'")
        if priority:
            conditions.append(f"Priority = '{priority.value}'")
        if account_id:
            conditions.append(f"AccountId = '{account_id}'")
        where = " AND ".join(conditions) if conditions else None
        soql = self._build_soql(CASE_FIELDS, where=where,
                                limit=limit, offset=offset)
        records = self._execute_query(soql)
        return [self._to_response(r) for r in records]

    def get_case(self, case_id: str) -> CaseResponse:
        record = self._get_by_id(case_id)
        return self._to_response(record)

    def create_case(self, data: CaseCreate) -> CaseResponse:
        payload = self._to_sf_payload(data.model_dump(exclude_none=True))
        new_id = self._create(payload)
        return self.get_case(new_id)

    def update_case(
        self, case_id: str, data: CaseUpdate
    ) -> CaseResponse:
        payload = self._to_sf_payload(
            data.model_dump(exclude_none=True)
        )
        self._update(case_id, payload)
        return self.get_case(case_id)

    def delete_case(self, case_id: str) -> bool:
        return self._delete(case_id)

    @staticmethod
    def _to_sf_payload(data: dict) -> dict:
        mapping = {
            "subject": "Subject",
            "status": "Status",
            "priority": "Priority",
            "description": "Description",
            "account_id": "AccountId",
            "contact_id": "ContactId",
            "origin": "Origin",
        }
        payload = {}
        for k, v in data.items():
            if k in mapping and v is not None:
                sf_key = mapping[k]
                payload[sf_key] = v.value if hasattr(v, "value") else v
        return payload

    @staticmethod
    def _to_response(record: dict) -> CaseResponse:
        return CaseResponse(
            id=record.get("Id", ""),
            case_number=record.get("CaseNumber"),
            subject=record.get("Subject", ""),
            status=record.get("Status", "New"),
            priority=record.get("Priority", "Medium"),
            description=record.get("Description"),
            account_id=record.get("AccountId"),
            contact_id=record.get("ContactId"),
            origin=record.get("Origin"),
            is_closed=record.get("IsClosed"),
            created_date=str(record.get("CreatedDate", "")),
            last_modified_date=str(record.get("LastModifiedDate", "")),
        )
