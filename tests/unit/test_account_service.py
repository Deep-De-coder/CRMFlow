import pytest
from unittest.mock import MagicMock
from app.services.account_service import AccountService
from app.models.account import AccountCreate, AccountUpdate
from app.salesforce.exceptions import RecordNotFoundError
from simple_salesforce.exceptions import SalesforceResourceNotFound


@pytest.mark.unit
class TestAccountService:

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_sf = MagicMock()
        self.mock_client.sf = self.mock_sf
        self.service = AccountService(self.mock_client)

    def test_list_accounts_returns_list(self, sample_account_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_account_record]
        }
        results = self.service.list_accounts()
        assert len(results) == 1
        assert results[0].name == "Acme Corp"
        assert results[0].id == "001ABC123"

    def test_list_accounts_with_industry_filter(self, sample_account_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_account_record]
        }
        self.service.list_accounts(industry="Technology")
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "Industry = 'Technology'" in call_args

    def test_list_accounts_empty_returns_empty_list(self):
        self.mock_sf.query_all.return_value = {"records": []}
        results = self.service.list_accounts()
        assert results == []

    def test_get_account_success(self, sample_account_record):
        self.mock_sf.Account.get.return_value = sample_account_record
        result = self.service.get_account("001ABC123")
        assert result.id == "001ABC123"
        assert result.name == "Acme Corp"
        assert result.industry == "Technology"

    def test_get_account_not_found_raises_error(self):
        self.mock_sf.Account.get.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError) as exc:
            self.service.get_account("001NOTFOUND")
        assert "001NOTFOUND" in exc.value.message

    def test_create_account_success(self, sample_account_record):
        self.mock_sf.Account.create.return_value = {
            "success": True, "id": "001ABC123"
        }
        self.mock_sf.Account.get.return_value = sample_account_record
        data = AccountCreate(
            name="Acme Corp",
            industry="Technology",
            phone="555-0100",
        )
        result = self.service.create_account(data)
        assert result.id == "001ABC123"
        create_call = self.mock_sf.Account.create.call_args[0][0]
        assert create_call["Name"] == "Acme Corp"
        assert create_call["Industry"] == "Technology"

    def test_create_account_maps_fields_correctly(self):
        self.mock_sf.Account.create.return_value = {
            "success": True, "id": "001NEW"
        }
        self.mock_sf.Account.get.return_value = {
            "Id": "001NEW", "Name": "New Co",
            "Industry": None, "Phone": None,
            "Website": None, "BillingCity": "Austin",
            "BillingCountry": "US", "NumberOfEmployees": None,
            "AnnualRevenue": None, "Description": None,
            "CreatedDate": "", "LastModifiedDate": "",
        }
        data = AccountCreate(
            name="New Co",
            billing_city="Austin",
            billing_country="US",
        )
        self.service.create_account(data)
        payload = self.mock_sf.Account.create.call_args[0][0]
        assert "BillingCity" in payload
        assert "BillingCountry" in payload
        assert "Name" in payload

    def test_update_account_success(self, sample_account_record):
        self.mock_sf.Account.update.return_value = 204
        self.mock_sf.Account.get.return_value = sample_account_record
        data = AccountUpdate(phone="555-9999")
        result = self.service.update_account("001ABC123", data)
        assert result.id == "001ABC123"
        update_call = self.mock_sf.Account.update.call_args[0]
        assert update_call[0] == "001ABC123"
        assert update_call[1]["Phone"] == "555-9999"

    def test_update_account_not_found(self):
        self.mock_sf.Account.update.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.update_account("001NOTFOUND", AccountUpdate(phone="x"))

    def test_delete_account_success(self):
        self.mock_sf.Account.delete.return_value = 204
        result = self.service.delete_account("001ABC123")
        assert result is True

    def test_delete_account_not_found(self):
        self.mock_sf.Account.delete.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.delete_account("001NOTFOUND")

    def test_search_accounts_builds_like_query(self, sample_account_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_account_record]
        }
        self.service.search_accounts("Acme")
        query = self.mock_sf.query_all.call_args[0][0]
        assert "Name LIKE '%Acme%'" in query
