from app.services.base import BaseService
from app.models.opportunity import (
    OpportunityCreate, OpportunityUpdate,
    OpportunityResponse, OpportunityStage
)
from typing import Optional

OPPORTUNITY_FIELDS = [
    "Id", "Name", "StageName", "CloseDate", "Amount",
    "AccountId", "Probability", "Description", "LeadSource",
    "IsClosed", "IsWon", "CreatedDate", "LastModifiedDate",
]


class OpportunityService(BaseService):
    """
    Service layer for Salesforce Opportunity operations.
    Supports filtering by stage and account.
    Includes pipeline summary computation.
    """

    sf_object = "Opportunity"

    def list_opportunities(
        self,
        stage: Optional[OpportunityStage] = None,
        account_id: Optional[str] = None,
        is_closed: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OpportunityResponse]:
        conditions = []
        if stage:
            conditions.append(f"StageName = '{stage.value}'")
        if account_id:
            conditions.append(f"AccountId = '{account_id}'")
        if is_closed is not None:
            flag = "true" if is_closed else "false"
            conditions.append(f"IsClosed = {flag}")
        where = " AND ".join(conditions) if conditions else None
        soql = self._build_soql(OPPORTUNITY_FIELDS, where=where,
                                limit=limit, offset=offset)
        records = self._execute_query(soql)
        return [self._to_response(r) for r in records]

    def get_opportunity(self, opp_id: str) -> OpportunityResponse:
        record = self._get_by_id(opp_id)
        return self._to_response(record)

    def create_opportunity(
        self, data: OpportunityCreate
    ) -> OpportunityResponse:
        payload = self._to_sf_payload(data.model_dump(exclude_none=True))
        new_id = self._create(payload)
        return self.get_opportunity(new_id)

    def update_opportunity(
        self, opp_id: str, data: OpportunityUpdate
    ) -> OpportunityResponse:
        payload = self._to_sf_payload(
            data.model_dump(exclude_none=True)
        )
        self._update(opp_id, payload)
        return self.get_opportunity(opp_id)

    def delete_opportunity(self, opp_id: str) -> bool:
        return self._delete(opp_id)

    def get_pipeline_summary(self) -> dict:
        """
        Returns open pipeline totals grouped by stage.
        Demonstrates SOQL aggregation.
        """
        soql = (
            "SELECT StageName, COUNT(Id) total, SUM(Amount) value "
            "FROM Opportunity "
            "WHERE IsClosed = false "
            "GROUP BY StageName"
        )
        records = self._execute_query(soql)
        return {
            r["StageName"]: {
                "count": r["total"],
                "total_value": r["value"] or 0,
            }
            for r in records
        }

    @staticmethod
    def _to_sf_payload(data: dict) -> dict:
        mapping = {
            "name": "Name",
            "stage_name": "StageName",
            "close_date": "CloseDate",
            "amount": "Amount",
            "account_id": "AccountId",
            "probability": "Probability",
            "description": "Description",
            "lead_source": "LeadSource",
        }
        payload = {}
        for k, v in data.items():
            if k in mapping and v is not None:
                sf_key = mapping[k]
                payload[sf_key] = v.value if hasattr(v, "value") else v
        return payload

    @staticmethod
    def _to_response(record: dict) -> OpportunityResponse:
        return OpportunityResponse(
            id=record.get("Id", ""),
            name=record.get("Name", ""),
            stage_name=record.get("StageName", "Prospecting"),
            close_date=str(record.get("CloseDate", "")),
            amount=record.get("Amount"),
            account_id=record.get("AccountId"),
            probability=record.get("Probability"),
            description=record.get("Description"),
            lead_source=record.get("LeadSource"),
            is_closed=record.get("IsClosed"),
            is_won=record.get("IsWon"),
            created_date=str(record.get("CreatedDate", "")),
            last_modified_date=str(record.get("LastModifiedDate", "")),
        )
