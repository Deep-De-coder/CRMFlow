import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.salesforce.client import get_sf_client, SalesforceClient
from simple_salesforce.exceptions import SalesforceResourceNotFound


def make_mock_client(sample_record: dict = None):
    client = MagicMock(spec=SalesforceClient)
    mock_sf = MagicMock()
    client.sf = mock_sf
    if sample_record:
        mock_sf.query_all.return_value = {"records": [sample_record]}
        mock_sf.Contact.get.return_value = sample_record
        mock_sf.Contact.create.return_value = {
            "success": True, "id": sample_record["Id"]
        }
        mock_sf.Contact.update.return_value = 204
        mock_sf.Contact.delete.return_value = 204
    return client, mock_sf


@pytest.mark.integration
class TestContactsAPI:

    def setup_method(self):
        self.client = TestClient(app)

    def test_list_contacts_success(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/contacts/")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert data[0]["id"] == "003XYZ789"
            assert data[0]["last_name"] == "Doe"
        finally:
            app.dependency_overrides.clear()

    def test_list_contacts_with_account_filter(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/contacts/?account_id=001ABC123")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "AccountId = '001ABC123'" in query
        finally:
            app.dependency_overrides.clear()

    def test_get_contact_success(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/contacts/003XYZ789")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "003XYZ789"
            assert data["email"] == "jane.doe@acme.example.com"
        finally:
            app.dependency_overrides.clear()

    def test_get_contact_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Contact.get.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/contacts/003NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_create_contact_success(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.post("/contacts/", json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@acme.example.com",
                "account_id": "001ABC123",
            })
            assert response.status_code == 201
            data = response.json()
            assert data["last_name"] == "Doe"
        finally:
            app.dependency_overrides.clear()

    def test_create_contact_missing_last_name_returns_422(self):
        response = self.client.post("/contacts/", json={
            "first_name": "Jane",
            "email": "jane@example.com",
        })
        assert response.status_code == 422

    def test_update_contact_success(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/contacts/003XYZ789", json={
                "title": "CTO",
            })
            assert response.status_code == 200
            update_call = mock_sf.Contact.update.call_args[0]
            assert update_call[0] == "003XYZ789"
            assert update_call[1]["Title"] == "CTO"
        finally:
            app.dependency_overrides.clear()

    def test_update_contact_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Contact.update.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/contacts/003NOTFOUND", json={
                "title": "CTO",
            })
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_delete_contact_success(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/contacts/003XYZ789")
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()

    def test_delete_contact_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Contact.delete.side_effect = SalesforceResourceNotFound(
            "Contact", "003NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/contacts/003NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_list_contacts_pagination(self, sample_contact_record):
        mock_client, mock_sf = make_mock_client(sample_contact_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/contacts/?limit=5&offset=10")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "LIMIT 5" in query
            assert "OFFSET 10" in query
        finally:
            app.dependency_overrides.clear()
