from app.services.base import BaseService
from app.salesforce.client import SalesforceClient
from app.models.account import (
    AccountCreate, AccountUpdate, AccountResponse
)
from typing import Optional
import logging

logger = logging.getLogger(__name__)

ACCOUNT_FIELDS = [
    "Id", "Name", "Industry", "Phone", "Website",
    "BillingCity", "BillingCountry", "NumberOfEmployees",
    "AnnualRevenue", "Description", "CreatedDate", "LastModifiedDate",
]


class AccountService(BaseService):
    """
    Service layer for Salesforce Account operations.
    Handles CRUD and search with field mapping between
    Salesforce API names and our API models.
    """

    sf_object = "Account"

    def list_accounts(
        self,
        industry: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AccountResponse]:
        where = None
        if industry:
            where = f"Industry = '{industry}'"
        soql = self._build_soql(ACCOUNT_FIELDS, where=where,
                                limit=limit, offset=offset)
        records = self._execute_query(soql)
        return [self._to_response(r) for r in records]

    def get_account(self, account_id: str) -> AccountResponse:
        record = self._get_by_id(account_id)
        return self._to_response(record)

    def create_account(self, data: AccountCreate) -> AccountResponse:
        payload = self._to_sf_payload(data.model_dump(exclude_none=True))
        new_id = self._create(payload)
        return self.get_account(new_id)

    def update_account(
        self, account_id: str, data: AccountUpdate
    ) -> AccountResponse:
        payload = self._to_sf_payload(
            data.model_dump(exclude_none=True)
        )
        self._update(account_id, payload)
        return self.get_account(account_id)

    def delete_account(self, account_id: str) -> bool:
        return self._delete(account_id)

    def search_accounts(self, name: str) -> list[AccountResponse]:
        where = f"Name LIKE '%{name}%'"
        soql = self._build_soql(ACCOUNT_FIELDS, where=where, limit=25)
        records = self._execute_query(soql)
        return [self._to_response(r) for r in records]

    @staticmethod
    def _to_sf_payload(data: dict) -> dict:
        mapping = {
            "name": "Name",
            "industry": "Industry",
            "phone": "Phone",
            "website": "Website",
            "billing_city": "BillingCity",
            "billing_country": "BillingCountry",
            "number_of_employees": "NumberOfEmployees",
            "annual_revenue": "AnnualRevenue",
            "description": "Description",
        }
        return {
            mapping[k]: v
            for k, v in data.items()
            if k in mapping and v is not None
        }

    @staticmethod
    def _to_response(record: dict) -> AccountResponse:
        return AccountResponse(
            id=record.get("Id", ""),
            name=record.get("Name", ""),
            industry=record.get("Industry"),
            phone=record.get("Phone"),
            website=record.get("Website"),
            billing_city=record.get("BillingCity"),
            billing_country=record.get("BillingCountry"),
            number_of_employees=record.get("NumberOfEmployees"),
            annual_revenue=record.get("AnnualRevenue"),
            description=record.get("Description"),
            created_date=str(record.get("CreatedDate", "")),
            last_modified_date=str(record.get("LastModifiedDate", "")),
        )
