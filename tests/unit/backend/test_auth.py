import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.unit
@pytest.mark.api
def test_sso_providers_empty(monkeypatch):
    # Keine Provider konfiguriert
    monkeypatch.setenv("SSO_GOOGLE_ENABLED", "false")
    monkeypatch.setenv("SSO_MICROSOFT_ENABLED", "false")
    monkeypatch.setenv("SSO_GITHUB_ENABLED", "false")
    monkeypatch.setenv("SSO_SAML_ENABLED", "false")
    monkeypatch.setenv("SSO_OIDC_ENABLED", "false")
    response = client.get("/api/v1/auth/sso/providers")
    assert response.status_code == 200  # noqa: S101
    assert response.json()["providers"] == []  # noqa: S101


@pytest.mark.unit
@pytest.mark.api
def test_sso_providers_google(monkeypatch):
    monkeypatch.setenv("SSO_GOOGLE_ENABLED", "true")
    monkeypatch.setenv("SSO_GOOGLE_CLIENT_ID", "test-google-client-id")
    response = client.get("/api/v1/auth/sso/providers")
    assert response.status_code == 200  # noqa: S101
    providers = response.json()["providers"]
    assert any(p["id"] == "google" for p in providers)  # noqa: S101


@pytest.mark.unit
@pytest.mark.api
def test_sso_login_redirect(monkeypatch):
    monkeypatch.setenv("SSO_GOOGLE_ENABLED", "true")
    monkeypatch.setenv("SSO_GOOGLE_CLIENT_ID", "test-google-client-id")
    response = client.get("/api/v1/auth/sso/login/google")
    assert response.status_code == 200  # noqa: S101
    assert "redirect_url" in response.json()  # noqa: S101


@pytest.mark.unit
@pytest.mark.api
def test_sso_login_not_configured(monkeypatch):
    monkeypatch.setenv("SSO_GOOGLE_ENABLED", "false")
    response = client.get("/api/v1/auth/sso/login/google")
    assert response.status_code == 400  # noqa: S101
    assert "not configured" in response.json()["detail"].lower()  # noqa: S101


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.asyncio
async def test_login_fail():
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpass"},
    )
    assert response.status_code in [400, 401, 422]  # noqa: S101
