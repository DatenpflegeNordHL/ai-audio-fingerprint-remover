from __future__ import annotations

import hashlib

from tests.web.helpers import auth_header, basic_auth_header, call_app, multipart_body, prepare_env


def test_health_works_without_auth(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_remains_available_without_beta_password_config(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/")

    assert response.status_code == 200


def test_dashboard_requires_safe_beta_password_when_configured(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    monkeypatch.setenv("AQH_BETA_PASSWORD", "private-beta-placeholder")

    missing = call_app("GET", "/")
    wrong = call_app("GET", "/", headers=basic_auth_header(password="wrong-password"))
    accepted = call_app("GET", "/", headers=basic_auth_header(password="private-beta-placeholder"))

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert accepted.status_code == 200
    encoded = wrong.body.decode("utf-8")
    assert "private-beta-placeholder" not in encoded
    assert "wrong-password" not in encoded


def test_dashboard_accepts_beta_password_hash(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    password = "hashed-private-beta-placeholder"
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    monkeypatch.setenv("AQH_BETA_PASSWORD_HASH", f"sha256:{digest}")

    response = call_app("GET", "/", headers=basic_auth_header(password=password))

    assert response.status_code == 200


def test_api_rejects_missing_token(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()

    response = call_app("POST", "/api/jobs", headers={"content-type": content_type}, body=body)

    assert response.status_code == 401
    encoded = response.body.decode("utf-8")
    assert "Bearer token is required" in encoded
    assert "test-token" not in encoded


def test_api_rejects_wrong_bearer_token(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header("wrong-token"), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 401
    encoded = response.body.decode("utf-8")
    assert "Bearer token was not accepted" in encoded
    assert "test-token" not in encoded
    assert "wrong-token" not in encoded


def test_api_returns_safe_error_when_server_token_is_not_configured(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    monkeypatch.delenv("AQH_WEB_TOKEN", raising=False)
    body, content_type = multipart_body()

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 503
    encoded = response.body.decode("utf-8")
    assert "bearer token is not configured" in encoded
    assert "test-token" not in encoded


def test_api_accepts_correct_bearer_token(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 201
    assert response.json()["status"] == "completed"
