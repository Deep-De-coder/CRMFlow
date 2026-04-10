import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.salesforce.client import SalesforceClient


@pytest.fixture
def mock_sf_client():
    """
    Returns a MagicMock SalesforceClient.
    Patches get_sf_client so no real Salesforce
    connection is attempted in unit tests.
    """
    client = MagicMock(spec=SalesforceClient)
    mock_sf = MagicMock()
    client.sf = mock_sf
    return client, mock_sf


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def sample_account_record():
    return {
        "Id": "001ABC123",
        "Name": "Acme Corp",
        "Industry": "Technology",
        "Phone": "555-0100",
        "Website": "https://acme.example.com",
        "BillingCity": "San Francisco",
        "BillingCountry": "US",
        "NumberOfEmployees": 500,
        "AnnualRevenue": 10000000.0,
        "Description": "Test account",
        "CreatedDate": "2026-01-01T00:00:00.000+0000",
        "LastModifiedDate": "2026-01-15T00:00:00.000+0000",
        "attributes": {"type": "Account"},
    }


@pytest.fixture
def sample_contact_record():
    return {
        "Id": "003XYZ789",
        "FirstName": "Jane",
        "LastName": "Doe",
        "Email": "jane.doe@acme.example.com",
        "Phone": "555-0101",
        "Title": "VP Engineering",
        "Department": "Engineering",
        "AccountId": "001ABC123",
        "CreatedDate": "2026-01-01T00:00:00.000+0000",
        "LastModifiedDate": "2026-01-15T00:00:00.000+0000",
        "attributes": {"type": "Contact"},
    }


@pytest.fixture
def sample_opportunity_record():
    return {
        "Id": "006OPP001",
        "Name": "Acme Enterprise Deal",
        "StageName": "Prospecting",
        "CloseDate": "2026-06-30",
        "Amount": 75000.0,
        "AccountId": "001ABC123",
        "Probability": 25.0,
        "Description": "Big deal",
        "LeadSource": "Web",
        "IsClosed": False,
        "IsWon": False,
        "CreatedDate": "2026-01-01T00:00:00.000+0000",
        "LastModifiedDate": "2026-01-15T00:00:00.000+0000",
        "attributes": {"type": "Opportunity"},
    }


@pytest.fixture
def sample_case_record():
    return {
        "Id": "500CASE01",
        "CaseNumber": "00001001",
        "Subject": "Login issue",
        "Status": "New",
        "Priority": "High",
        "Description": "Cannot log in",
        "AccountId": "001ABC123",
        "ContactId": "003XYZ789",
        "Origin": "Web",
        "IsClosed": False,
        "CreatedDate": "2026-01-01T00:00:00.000+0000",
        "LastModifiedDate": "2026-01-15T00:00:00.000+0000",
        "attributes": {"type": "Case"},
    }
