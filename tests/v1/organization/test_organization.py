from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid_extensions import uuid7
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.models import User
from api.v1.models.organization import Organization
from api.v1.services.user import UserService
from api.v1.services.organization import organization_service
from main import app

client = TestClient(app)

# Create a mock database session
@pytest.fixture
def db_session_mock():
    db = MagicMock()
    yield db
    db.close()

# Override the get_db dependency
@pytest.fixture(autouse=True)
def override_get_db(db_session_mock):
    def _get_db_override():
        yield db_session_mock

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# Mock the current user function
@pytest.fixture
def mock_get_current_user():
    with patch.object(UserService, 'get_current_user', return_value={"id": 1, "email": "test@example.com"}):
        yield

def test_get_organization_success(db_session_mock, mock_get_current_user):
    mock_organization = MagicMock(spec=Organization)
    mock_organization.id = "Str"
    mock_organization.company_name = "Mock Org 1"
    mock_organization.company_email = "olawaleisaacjohn@gmail.com"
    mock_organization.industry = "Technology"
    mock_organization.organization_type = "Private"
    mock_organization.country = "Country"
    mock_organization.state = "State"
    mock_organization.address = "123 Street"
    mock_organization.lga = "LGA"
    mock_organization.created_at = datetime.now()
    mock_organization.updated_at = datetime.now()

    db_session_mock.query().filter().first.return_value = mock_organization

    response = client.get("/api/v1/organizations/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["status_code"] == 200
    assert data["data"]["id"] == "Str"
    assert data["data"]["company_name"] == "Mock Org 1"
    assert data["data"]["company_email"] == "olawaleisaacjohn@gmail.com"
    assert data["data"]["industry"] == "Technology"
    assert data["data"]["organization"] == "Private"
    assert data["data"]["state"] == "State"
    assert data["data"]["address"] == "123 Street"
    assert data["data"]["lga"] == "LGA"

def test_get_organization_not_found(db_session_mock, mock_get_current_user):
    db_session_mock.query().filter().first.return_value = None

    response = client.get("/api/v1/organizations/999", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "Organization not found"
    assert data["status_code"] == 404
    assert not data["success"]

def test_get_organization_invalid_id(db_session_mock, mock_get_current_user):
    response = client.get("/api/v1/organizations/abc", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 422  # Unprocessable Entity due to validation error
