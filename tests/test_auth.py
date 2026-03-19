"""
test_auth.py
Tests for login, register, logout routes.
"""

import pytest


class TestRegister:

    def test_register_page_loads(self, client):
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Create an account" in response.data

    def test_register_success(self, client, app):
        response = client.post("/register", data={
            "email":            "newuser@test.com",
            "full_name":        "New User",
            "password":         "pass1234",
            "confirm_password": "pass1234",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Log in" in response.data  # redirected to login

        # cleanup
        from app.models.user import User
        with app.app_context():
            u = User.query_by_email("newuser@test.com")
            if u:
                u.delete()

    def test_register_password_mismatch(self, client):
        response = client.post("/register", data={
            "email":            "x@test.com",
            "full_name":        "X",
            "password":         "abc123",
            "confirm_password": "different",
        }, follow_redirects=True)
        assert b"Passwords do not match" in response.data

    def test_register_short_password(self, client):
        response = client.post("/register", data={
            "email":            "x@test.com",
            "full_name":        "X",
            "password":         "ab",
            "confirm_password": "ab",
        }, follow_redirects=True)
        assert b"6 characters" in response.data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/register", data={
            "email":            "test@example.com",   # same as test_user
            "full_name":        "Another",
            "password":         "pass1234",
            "confirm_password": "pass1234",
        }, follow_redirects=True)
        assert b"already registered" in response.data


class TestLogin:

    def test_login_page_loads(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Welcome back" in response.data

    def test_login_success(self, client, test_user):
        response = client.post("/login", data={
            "email":    "test@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Dashboard" in response.data or b"Hi," in response.data

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/login", data={
            "email":    "test@example.com",
            "password": "wrongpassword",
        }, follow_redirects=True)
        assert b"Incorrect email or password" in response.data

    def test_login_unknown_email(self, client):
        response = client.post("/login", data={
            "email":    "nobody@nowhere.com",
            "password": "whatever",
        }, follow_redirects=True)
        assert b"Incorrect email or password" in response.data


class TestLogout:

    def test_logout_redirects(self, logged_in_client):
        response = logged_in_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"logged out" in response.data

    def test_logout_requires_login(self, client):
        response = client.get("/logout", follow_redirects=True)
        # should redirect to login page
        assert b"Log in" in response.data or response.status_code == 200
