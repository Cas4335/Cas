"""
E2E happy path test.

Requires the full stack to be running.
Set E2E_API_URL to the API base URL (default: http://localhost:8000).

Run with: pytest tests/e2e/ -v --e2e
"""

import os
import pytest
import httpx

API_URL = os.environ.get("E2E_API_URL", "http://localhost:8000")

pytestmark = pytest.mark.skipif(
    os.environ.get("E2E", "0") != "1",
    reason="Set E2E=1 to run end-to-end tests against a live stack",
)


@pytest.fixture
def api():
    return httpx.Client(base_url=API_URL, timeout=60)


@pytest.fixture
def auth_token(api):
    res = api.post("/auth/login", json={"email": "admin@example.com", "password": "changeme123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


def test_health(api):
    res = api.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_login(api):
    res = api.post("/auth/login", json={"email": "admin@example.com", "password": "changeme123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data


def test_me(api, auth_token):
    res = api.get("/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "admin@example.com"
    assert "admin" in data["roles"]


def test_chat_returns_response(api, auth_token):
    """Admin can send a question and get a response (may be uncertainty if no data indexed)."""
    res = api.post(
        "/chat/",
        json={"query": "What is the vacation policy?"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "citations" in data
    assert isinstance(data["grounded"], bool)


def test_chat_returns_citations_when_grounded(api, auth_token):
    """If chunks are found, citations should be non-empty."""
    res = api.post(
        "/chat/",
        json={"query": "vacation days remote work policy"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    if data["grounded"]:
        assert len(data["citations"]) > 0
        for c in data["citations"]:
            assert "title" in c
            assert "source_path" in c
            assert "score" in c


def test_unauthorized_chat(api):
    """Chat without token should fail."""
    res = api.post("/chat/", json={"query": "test"})
    assert res.status_code in (401, 403)


def test_sources_list(api, auth_token):
    res = api.get("/sources/", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_audit_logs_admin_only(api, auth_token):
    res = api.get("/admin/audit-logs", headers={"Authorization": f"Bearer {auth_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
