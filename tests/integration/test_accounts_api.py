import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.salesforce.client import get_sf_client, SalesforceClient
from app.salesforce.exceptions import RecordNotFoundError


def make_mock_client(sample_record: dict = None):
    client = MagicMock(spec=SalesforceClient)
    mock_sf = MagicMock()
    client.sf = mock_sf
    if sample_record:
        mock_sf.query_all.return_value = {"records": [sample_record]}
        mock_sf.Account.get.return_value = sample_record
        mock_sf.Account.create.return_value = {
            "success": True, "id": sample_record["Id"]
        }
        mock_sf.Account.update.return_value = 204
        mock_sf.Account.delete.return_value = 204
    return client, mock_sf


@pytest.mark.integration
class TestAccountsAPI:

    def setup_method(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint(self):
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SalesforceSync"
        assert "/accounts" in data["endpoints"]

    def test_list_accounts_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert data[0]["id"] == "001ABC123"
            assert data[0]["name"] == "Acme Corp"
        finally:
            app.dependency_overrides.clear()

    def test_list_accounts_with_industry_query(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/?industry=Technology")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "Industry = 'Technology'" in query
        finally:
            app.dependency_overrides.clear()

    def test_get_account_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/001ABC123")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "001ABC123"
            assert data["industry"] == "Technology"
        finally:
            app.dependency_overrides.clear()

    def test_get_account_not_found(self):
        mock_client, mock_sf = make_mock_client()
        from simple_salesforce.exceptions import SalesforceResourceNotFound
        mock_sf.Account.get.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/001NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_create_account_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.post("/accounts/", json={
                "name": "Acme Corp",
                "industry": "Technology",
                "phone": "555-0100",
            })
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Acme Corp"
        finally:
            app.dependency_overrides.clear()

    def test_create_account_missing_name_returns_422(self):
        response = self.client.post("/accounts/", json={
            "industry": "Technology",
        })
        assert response.status_code == 422

    def test_update_account_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/accounts/001ABC123", json={
                "phone": "555-9999",
            })
            assert response.status_code == 200
            update_call = mock_sf.Account.update.call_args[0]
            assert update_call[0] == "001ABC123"
            assert update_call[1]["Phone"] == "555-9999"
        finally:
            app.dependency_overrides.clear()

    def test_update_account_not_found(self):
        mock_client, mock_sf = make_mock_client()
        from simple_salesforce.exceptions import SalesforceResourceNotFound
        mock_sf.Account.update.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/accounts/001NOTFOUND", json={
                "phone": "555-9999",
            })
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_delete_account_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/accounts/001ABC123")
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()

    def test_delete_account_not_found(self):
        mock_client, mock_sf = make_mock_client()
        from simple_salesforce.exceptions import SalesforceResourceNotFound
        mock_sf.Account.delete.side_effect = SalesforceResourceNotFound(
            "Account", "001NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/accounts/001NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_search_accounts_success(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/search?name=Acme")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "LIKE '%Acme%'" in query
        finally:
            app.dependency_overrides.clear()

    def test_list_accounts_pagination(self, sample_account_record):
        mock_client, mock_sf = make_mock_client(sample_account_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/accounts/?limit=10&offset=20")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "LIMIT 10" in query
            assert "OFFSET 20" in query
        finally:
            app.dependency_overrides.clear()
