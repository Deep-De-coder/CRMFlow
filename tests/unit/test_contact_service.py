import pytest
from unittest.mock import MagicMock
from app.services.contact_service import ContactService
from app.models.contact import ContactCreate, ContactUpdate
from app.salesforce.exceptions import RecordNotFoundError
from simple_salesforce.exceptions import SalesforceResourceNotFound


@pytest.mark.unit
class TestContactService:

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_sf = MagicMock()
        self.mock_client.sf = self.mock_sf
        self.service = ContactService(self.mock_client)

    def test_list_contacts_returns_list(self, sample_contact_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_contact_record]
        }
        results = self.service.list_contacts()
        assert len(results) == 1
        assert results[0].last_name == "Doe"
        assert results[0].id == "003XYZ789"

    def test_list_contacts_with_account_filter(self, sample_contact_record):
        self.mock_sf.query_all.return_value = {
            "records": [sample_contact_record]
        }
        self.service.list_contacts(account_id="001ABC123")
        call_args = self.mock_sf.query_all.call_args[0][0]
        assert "AccountId = '001ABC123'" in call_args

    def test_list_contacts_empty_returns_empty_list(self):
        self.mock_sf.query_all.return_value = {"records": []}
        results = self.service.list_contacts()
        assert results == []

    def test_get_contact_success(self, sample_contact_record):
        self.mock_sf.Contact.get.return_value = sample_contact_record
        result = self.service.get_contact("003XYZ789")
        assert result.id == "003XYZ789"
        assert result.first_name == "Jane"
        assert result.last_name == "Doe"
        assert result.email == "jane.doe@acme.example.com"

    def test_get_contact_not_found_raises_error(self):
        self.mock_sf.Contact.get.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError) as exc:
            self.service.get_contact("003NOTFOUND")
        assert "003NOTFOUND" in exc.value.message

    def test_create_contact_success(self, sample_contact_record):
        self.mock_sf.Contact.create.return_value = {
            "success": True, "id": "003XYZ789"
        }
        self.mock_sf.Contact.get.return_value = sample_contact_record
        data = ContactCreate(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@acme.example.com",
        )
        result = self.service.create_contact(data)
        assert result.id == "003XYZ789"
        create_call = self.mock_sf.Contact.create.call_args[0][0]
        assert create_call["LastName"] == "Doe"
        assert create_call["FirstName"] == "Jane"

    def test_create_contact_maps_fields_correctly(self):
        self.mock_sf.Contact.create.return_value = {
            "success": True, "id": "003NEW"
        }
        self.mock_sf.Contact.get.return_value = {
            "Id": "003NEW", "FirstName": "Bob", "LastName": "Smith",
            "Email": "bob@example.com", "Phone": None,
            "Title": "Manager", "Department": "Sales",
            "AccountId": "001ABC123",
            "CreatedDate": "", "LastModifiedDate": "",
        }
        data = ContactCreate(
            first_name="Bob",
            last_name="Smith",
            email="bob@example.com",
            title="Manager",
            department="Sales",
            account_id="001ABC123",
        )
        self.service.create_contact(data)
        payload = self.mock_sf.Contact.create.call_args[0][0]
        assert payload["FirstName"] == "Bob"
        assert payload["LastName"] == "Smith"
        assert payload["AccountId"] == "001ABC123"
        assert payload["Title"] == "Manager"

    def test_update_contact_success(self, sample_contact_record):
        self.mock_sf.Contact.update.return_value = 204
        self.mock_sf.Contact.get.return_value = sample_contact_record
        data = ContactUpdate(phone="555-9999")
        result = self.service.update_contact("003XYZ789", data)
        assert result.id == "003XYZ789"
        update_call = self.mock_sf.Contact.update.call_args[0]
        assert update_call[0] == "003XYZ789"
        assert update_call[1]["Phone"] == "555-9999"

    def test_update_contact_not_found(self):
        self.mock_sf.Contact.update.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.update_contact(
                "003NOTFOUND", ContactUpdate(phone="x")
            )

    def test_delete_contact_success(self):
        self.mock_sf.Contact.delete.return_value = 204
        result = self.service.delete_contact("003XYZ789")
        assert result is True

    def test_delete_contact_not_found(self):
        self.mock_sf.Contact.delete.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        with pytest.raises(RecordNotFoundError):
            self.service.delete_contact("003NOTFOUND")

    def test_to_response_handles_none_fields(self):
        record = {
            "Id": "003MIN",
            "FirstName": None,
            "LastName": "Solo",
            "Email": None,
            "Phone": None,
            "Title": None,
            "Department": None,
            "AccountId": None,
            "CreatedDate": None,
            "LastModifiedDate": None,
        }
        result = ContactService._to_response(record)
        assert result.id == "003MIN"
        assert result.last_name == "Solo"
        assert result.first_name is None
        assert result.account_id is None
