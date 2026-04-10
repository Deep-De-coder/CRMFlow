import pytest
from unittest.mock import MagicMock
from app.services.opportunity_service import OpportunityService
from app.models.opportunity import (
    OpportunityCreate, OpportunityUpdate, OpportunityStage
)
from app.salesforce.exceptions import RecordNotFoundError
from simple_salesforce.exceptions import SalesforceResourceNotFound


@pytest.mark.unit
class TestOpportunityService:

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_sf = MagicMock()
        self.mock_client.sf = self.mock_sf
        self.service = OpportunityService(self.mock_client)

    def test_list_opportunities_returns_list(self, sample_opportunity_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_opportunity_record]
        }
        results = self.service.list_opportunities()
        assert len(results) == 1
        assert results[0].name == "Acme Enterprise Deal"
        assert results[0].id == "006OPP001"

    def test_list_opportunities_with_stage_filter(self, sample_opportunity_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_opportunity_record]
        }
        self.service.list_opportunities(stage=OpportunityStage.PROSPECTING)
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "StageName = 'Prospecting'" in call_args

    def test_list_opportunities_with_account_filter(self, sample_opportunity_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_opportunity_record]
        }
        self.service.list_opportunities(account_id="001ABC123")
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "AccountId = '001ABC123'" in call_args

    def test_list_opportunities_is_closed_false(self, sample_opportunity_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_opportunity_record]
        }
        self.service.list_opportunities(is_closed=False)
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "IsClosed = false" in call_args

    def test_list_opportunities_is_closed_true(self):
        self.mock_sf.query_all.return_value = {"records": []}
        self.service.list_opportunities(is_closed=True)
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "IsClosed = true" in call_args

    def test_list_opportunities_combined_filters(self, sample_opportunity_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_opportunity_record]
        }
        self.service.list_opportunities(
            stage=OpportunityStage.PROSPECTING,
            account_id="001ABC123",
        )
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "StageName = 'Prospecting'" in call_args
        assert "AccountId = '001ABC123'" in call_args
        assert " AND " in call_args

    def test_get_opportunity_success(self, sample_opportunity_record):
        self.mock_sf.Opportunity.get.return_value = sample_opportunity_record
        result = self.service.get_opportunity("006OPP001")
        assert result.id == "006OPP001"
        assert result.name == "Acme Enterprise Deal"
        assert result.stage_name == OpportunityStage.PROSPECTING
        assert result.amount == 75000.0

    def test_get_opportunity_not_found(self):
        self.mock_sf.Opportunity.get.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError) as exc:
            self.service.get_opportunity("006NOTFOUND")
        assert "006NOTFOUND" in exc.value.message

    def test_create_opportunity_success(self, sample_opportunity_record):
        self.mock_sf.Opportunity.create.return_value = {
            "success": True, "id": "006OPP001"
        }
        self.mock_sf.Opportunity.get.return_value = sample_opportunity_record
        data = OpportunityCreate(
            name="Acme Enterprise Deal",
            stage_name=OpportunityStage.PROSPECTING,
            close_date="2026-06-30",
            amount=75000.0,
            account_id="001ABC123",
        )
        result = self.service.create_opportunity(data)
        assert result.id == "006OPP001"
        create_call = self.mock_sf.Opportunity.create.call_args[0][0]
        assert create_call["Name"] == "Acme Enterprise Deal"
        assert create_call["StageName"] == "Prospecting"
        assert create_call["CloseDate"] == "2026-06-30"

    def test_create_opportunity_stage_serialized_as_value(self):
        self.mock_sf.Opportunity.create.return_value = {
            "success": True, "id": "006NEW"
        }
        self.mock_sf.Opportunity.get.return_value = {
            "Id": "006NEW", "Name": "Deal",
            "StageName": "Closed Won", "CloseDate": "2026-12-31",
            "Amount": None, "AccountId": None, "Probability": None,
            "Description": None, "LeadSource": None,
            "IsClosed": True, "IsWon": True,
            "CreatedDate": "", "LastModifiedDate": "",
        }
        data = OpportunityCreate(
            name="Deal",
            stage_name=OpportunityStage.CLOSED_WON,
            close_date="2026-12-31",
        )
        self.service.create_opportunity(data)
        payload = self.mock_sf.Opportunity.create.call_args[0][0]
        assert payload["StageName"] == "Closed Won"

    def test_update_opportunity_success(self, sample_opportunity_record):
        self.mock_sf.Opportunity.update.return_value = 204
        self.mock_sf.Opportunity.get.return_value = sample_opportunity_record
        data = OpportunityUpdate(amount=90000.0)
        result = self.service.update_opportunity("006OPP001", data)
        assert result.id == "006OPP001"
        update_call = self.mock_sf.Opportunity.update.call_args[0]
        assert update_call[0] == "006OPP001"
        assert update_call[1]["Amount"] == 90000.0

    def test_update_opportunity_not_found(self):
        self.mock_sf.Opportunity.update.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.update_opportunity(
                "006NOTFOUND", OpportunityUpdate(amount=1000.0)
            )

    def test_delete_opportunity_success(self):
        self.mock_sf.Opportunity.delete.return_value = 204
        result = self.service.delete_opportunity("006OPP001")
        assert result is True

    def test_delete_opportunity_not_found(self):
        self.mock_sf.Opportunity.delete.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.delete_opportunity("006NOTFOUND")

    def test_get_pipeline_summary_returns_dict(self):
        self.mock_sf.query_all.return_value = {
            "records": [
                {"StageName": "Prospecting", "total": 5, "value": 250000.0},
                {"StageName": "Qualification", "total": 3, "value": 150000.0},
            ]
        }
        result = self.service.get_pipeline_summary()
        assert "Prospecting" in result
        assert result["Prospecting"]["count"] == 5
        assert result["Prospecting"]["total_value"] == 250000.0
        assert result["Qualification"]["count"] == 3

    def test_get_pipeline_summary_handles_null_amount(self):
        self.mock_sf.query_all.return_value = {
            "records": [
                {"StageName": "Prospecting", "total": 2, "value": None},
            ]
        }
        result = self.service.get_pipeline_summary()
        assert result["Prospecting"]["total_value"] == 0
