"""
conftest.py
Shared pytest fixtures using MockFirestore.
"""

import pytest
from mockfirestore import MockFirestore
from config import TestConfig
from app import create_app

@pytest.fixture(scope="session")
def app():
    """Create app with mock firestore."""
    app = create_app(TestConfig)
    yield app

@pytest.fixture(scope="function")
def db(app, monkeypatch):
    """Set up mock firestore for each test."""
    mock_db = MockFirestore()
    import app as main_app
    # Because our models lazy-load `from app import db`, 
    # replacing it here safely intercepts all DB calls globally for the test.
    monkeypatch.setattr(main_app, "db", mock_db)
    yield mock_db
    mock_db.reset()

@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def runner(app):
    """Flask CLI test runner."""
    return app.test_cli_runner()

@pytest.fixture(scope="function")
def test_user(db):
    """Create a fresh recruiter user in mock firestore."""
    from app.models.user import User

    user = User(email="test@example.com", full_name="Test User")
    user.set_password("password123")
    user.save()

    yield user

@pytest.fixture(scope="function")
def logged_in_client(client, test_user):
    """Test client that is already logged in as test_user."""
    client.post("/login", data={
        "email":    "test@example.com",
        "password": "password123",
    }, follow_redirects=True)
    return client
