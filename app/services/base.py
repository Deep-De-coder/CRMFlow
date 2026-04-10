from simple_salesforce import Salesforce
from simple_salesforce.exceptions import (
    SalesforceResourceNotFound,
    SalesforceMalformedRequest,
)
from app.salesforce.client import SalesforceClient
from app.salesforce.exceptions import (
    RecordNotFoundError,
    RecordCreateError,
    RecordUpdateError,
    RecordDeleteError,
    QueryError,
)
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """
    Abstract base service for Salesforce CRUD operations.
    All object-specific services inherit from this class.
    Encapsulates SOQL query building, error mapping, and
    response normalization.
    """

    sf_object: str = ""
    default_fields: list[str] = ["Id", "CreatedDate", "LastModifiedDate"]

    def __init__(self, client: SalesforceClient):
        self._client = client

    @property
    def sf(self) -> Salesforce:
        return self._client.sf

    @property
    def sobject(self):
        return getattr(self.sf, self.sf_object)

    def _build_soql(
        self,
        fields: list[str],
        where: str = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "CreatedDate DESC",
    ) -> str:
        field_str = ", ".join(fields)
        query = f"SELECT {field_str} FROM {self.sf_object}"
        if where:
            query += f" WHERE {where}"
        query += f" ORDER BY {order_by}"
        query += f" LIMIT {limit} OFFSET {offset}"
        return query

    def _execute_query(self, soql: str) -> list[dict]:
        try:
            result = self.sf.query_all(soql)
            return result.get("records", [])
        except Exception as e:
            raise QueryError(
                f"SOQL query failed on {self.sf_object}: {e}"
            ) from e

    def _get_by_id(self, record_id: str) -> dict:
        try:
            return self.sobject.get(record_id)
        except SalesforceResourceNotFound:
            raise RecordNotFoundError(
                f"{self.sf_object} with ID {record_id} not found"
            )
        except Exception as e:
            raise QueryError(
                f"Failed to fetch {self.sf_object} {record_id}: {e}"
            ) from e

    def _create(self, data: dict) -> str:
        try:
            result = self.sobject.create(data)
            if not result.get("success"):
                raise RecordCreateError(
                    f"Failed to create {self.sf_object}",
                    sf_error=result,
                )
            return result["id"]
        except RecordCreateError:
            raise
        except Exception as e:
            raise RecordCreateError(
                f"Failed to create {self.sf_object}: {e}"
            ) from e

    def _update(self, record_id: str, data: dict) -> bool:
        try:
            self.sobject.update(record_id, data)
            return True
        except SalesforceResourceNotFound:
            raise RecordNotFoundError(
                f"{self.sf_object} with ID {record_id} not found"
            )
        except Exception as e:
            raise RecordUpdateError(
                f"Failed to update {self.sf_object} {record_id}: {e}"
            ) from e

    def _delete(self, record_id: str) -> bool:
        try:
            self.sobject.delete(record_id)
            return True
        except SalesforceResourceNotFound:
            raise RecordNotFoundError(
                f"{self.sf_object} with ID {record_id} not found"
            )
        except Exception as e:
            raise RecordDeleteError(
                f"Failed to delete {self.sf_object} {record_id}: {e}"
            ) from e

    @staticmethod
    def _strip_sf_metadata(record: dict) -> dict:
        """Remove Salesforce metadata keys from record dict."""
        return {
            k: v for k, v in record.items()
            if k != "attributes"
        }
