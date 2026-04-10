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
        mock_sf.Opportunity.get.return_value = sample_record
        mock_sf.Opportunity.create.return_value = {
            "success": True, "id": sample_record["Id"]
        }
        mock_sf.Opportunity.update.return_value = 204
        mock_sf.Opportunity.delete.return_value = 204
    return client, mock_sf


@pytest.mark.integration
class TestOpportunitiesAPI:

    def setup_method(self):
        self.client = TestClient(app)

    def test_list_opportunities_success(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert data[0]["id"] == "006OPP001"
            assert data[0]["stage_name"] == "Prospecting"
        finally:
            app.dependency_overrides.clear()

    def test_list_opportunities_with_stage_filter(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/?stage=Prospecting")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "StageName = 'Prospecting'" in query
        finally:
            app.dependency_overrides.clear()

    def test_list_opportunities_with_is_closed_false(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/?is_closed=false")
            assert response.status_code == 200
            query = mock_sf.query_all.call_args[0][0]
            assert "IsClosed = false" in query
        finally:
            app.dependency_overrides.clear()

    def test_get_pipeline_summary(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.query_all.return_value = {
            "records": [
                {"StageName": "Prospecting", "total": 4, "value": 200000.0},
                {"StageName": "Qualification", "total": 2, "value": 80000.0},
            ]
        }
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/pipeline")
            assert response.status_code == 200
            data = response.json()
            assert "Prospecting" in data
            assert data["Prospecting"]["count"] == 4
            assert data["Prospecting"]["total_value"] == 200000.0
        finally:
            app.dependency_overrides.clear()

    def test_get_opportunity_success(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/006OPP001")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "006OPP001"
            assert data["amount"] == 75000.0
            assert data["is_closed"] is False
        finally:
            app.dependency_overrides.clear()

    def test_get_opportunity_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Opportunity.get.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.get("/opportunities/006NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_create_opportunity_success(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.post("/opportunities/", json={
                "name": "Acme Enterprise Deal",
                "stage_name": "Prospecting",
                "close_date": "2026-06-30",
                "amount": 75000.0,
                "account_id": "001ABC123",
            })
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Acme Enterprise Deal"
        finally:
            app.dependency_overrides.clear()

    def test_create_opportunity_missing_required_fields_returns_422(self):
        response = self.client.post("/opportunities/", json={
            "name": "Deal without stage",
        })
        assert response.status_code == 422

    def test_create_opportunity_invalid_stage_returns_422(self):
        response = self.client.post("/opportunities/", json={
            "name": "Bad Deal",
            "stage_name": "INVALID_STAGE",
            "close_date": "2026-06-30",
        })
        assert response.status_code == 422

    def test_update_opportunity_success(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/opportunities/006OPP001", json={
                "amount": 90000.0,
                "stage_name": "Qualification",
            })
            assert response.status_code == 200
            update_call = mock_sf.Opportunity.update.call_args[0]
            assert update_call[0] == "006OPP001"
            assert update_call[1]["Amount"] == 90000.0
            assert update_call[1]["StageName"] == "Qualification"
        finally:
            app.dependency_overrides.clear()

    def test_update_opportunity_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Opportunity.update.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.patch("/opportunities/006NOTFOUND", json={
                "amount": 1000.0,
            })
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_delete_opportunity_success(self, sample_opportunity_record):
        mock_client, mock_sf = make_mock_client(sample_opportunity_record)
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/opportunities/006OPP001")
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()

    def test_delete_opportunity_not_found(self):
        mock_client, mock_sf = make_mock_client()
        mock_sf.Opportunity.delete.side_effect = SalesforceResourceNotFound(
            "Opportunity", "006NOTFOUND"
        )
        app.dependency_overrides[get_sf_client] = lambda: mock_client
        try:
            response = self.client.delete("/opportunities/006NOTFOUND")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
