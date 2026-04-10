import pytest
from unittest.mock import MagicMock
from app.services.case_service import CaseService
from app.models.case import (
    CaseCreate, CaseUpdate, CaseStatus, CasePriority
)
from app.salesforce.exceptions import RecordNotFoundError
from simple_salesforce.exceptions import SalesforceResourceNotFound


@pytest.mark.unit
class TestCaseService:

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_sf = MagicMock()
        self.mock_client.sf = self.mock_sf
        self.service = CaseService(self.mock_client)

    def test_list_cases_returns_list(self, sample_case_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_case_record]
        }
        results = self.service.list_cases()
        assert len(results) == 1
        assert results[0].subject == "Login issue"
        assert results[0].id == "500CASE01"

    def test_list_cases_with_status_filter(self, sample_case_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_case_record]
        }
        self.service.list_cases(status=CaseStatus.NEW)
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "Status = 'New'" in call_args

    def test_list_cases_with_priority_filter(self, sample_case_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_case_record]
        }
        self.service.list_cases(priority=CasePriority.HIGH)
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "Priority = 'High'" in call_args

    def test_list_cases_with_account_filter(self, sample_case_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_case_record]
        }
        self.service.list_cases(account_id="001ABC123")
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "AccountId = '001ABC123'" in call_args

    def test_list_cases_combined_filters(self, sample_case_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_case_record]
        }
        self.service.list_cases(
            status=CaseStatus.NEW, priority=CasePriority.HIGH
        )
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "Status = 'New'" in call_args
        assert "Priority = 'High'" in call_args
        assert " AND " in call_args

    def test_get_case_success(self, sample_case_record):
        self.mock_sf.Case.get.return_value = sample_case_record
        result = self.service.get_case("500CASE01")
        assert result.id == "500CASE01"
        assert result.subject == "Login issue"
        assert result.case_number == "00001001"
        assert result.status == CaseStatus.NEW
        assert result.priority == CasePriority.HIGH

    def test_get_case_not_found(self):
        self.mock_sf.Case.get.side_effect = SalesforceResourceNotFound(
            "Case", "500NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError) as exc:
            self.service.get_case("500NOTFOUND")
        assert "500NOTFOUND" in exc.value.message

    def test_create_case_success(self, sample_case_record):
        self.mock_sf.Case.create.return_value = {
            "success": True, "id": "500CASE01"
        }
        self.mock_sf.Case.get.return_value = sample_case_record
        data = CaseCreate(
            subject="Login issue",
            status=CaseStatus.NEW,
            priority=CasePriority.HIGH,
            origin="Web",
            account_id="001ABC123",
            contact_id="003XYZ789",
        )
        result = self.service.create_case(data)
        assert result.id == "500CASE01"
        create_call = self.mock_sf.Case.create.call_args[0][0]
        assert create_call["Subject"] == "Login issue"
        assert create_call["Status"] == "New"
        assert create_call["Priority"] == "High"

    def test_create_case_enum_values_serialized(self):
        self.mock_sf.Case.create.return_value = {
            "success": True, "id": "500NEW"
        }
        self.mock_sf.Case.get.return_value = {
            "Id": "500NEW", "CaseNumber": "00001002",
            "Subject": "Escalated issue", "Status": "Escalated",
            "Priority": "High", "Description": None,
            "AccountId": None, "ContactId": None, "Origin": None,
            "IsClosed": False,
            "CreatedDate": "", "LastModifiedDate": "",
        }
        data = CaseCreate(
            subject="Escalated issue",
            status=CaseStatus.ESCALATED,
            priority=CasePriority.HIGH,
        )
        self.service.create_case(data)
        payload = self.mock_sf.Case.create.call_args[0][0]
        assert payload["Status"] == "Escalated"
        assert payload["Priority"] == "High"

    def test_update_case_success(self, sample_case_record):
        self.mock_sf.Case.update.return_value = 204
        self.mock_sf.Case.get.return_value = sample_case_record
        data = CaseUpdate(status=CaseStatus.WORKING)
        result = self.service.update_case("500CASE01", data)
        assert result.id == "500CASE01"
        update_call = self.mock_sf.Case.update.call_args[0]
        assert update_call[0] == "500CASE01"
        assert update_call[1]["Status"] == "Working"

    def test_update_case_not_found(self):
        self.mock_sf.Case.update.side_effect = SalesforceResourceNotFound(
            "Case", "500NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.update_case(
                "500NOTFOUND", CaseUpdate(status=CaseStatus.CLOSED)
            )

    def test_delete_case_success(self):
        self.mock_sf.Case.delete.return_value = 204
        result = self.service.delete_case("500CASE01")
        assert result is True

    def test_delete_case_not_found(self):
        self.mock_sf.Case.delete.side_effect = SalesforceResourceNotFound(
            "Case", "500NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.delete_case("500NOTFOUND")

    def test_to_response_handles_is_closed(self):
        record = {
            "Id": "500CLOSED",
            "CaseNumber": "00002000",
            "Subject": "Old issue",
            "Status": "Closed",
            "Priority": "Low",
            "Description": None,
            "AccountId": None,
            "ContactId": None,
            "Origin": None,
            "IsClosed": True,
            "CreatedDate": "2026-01-01",
            "LastModifiedDate": "2026-02-01",
        }
        result = CaseService._to_response(record)
        assert result.is_closed is True
        assert result.status == CaseStatus.CLOSED
