from __future__ import annotations

from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


def test_health_works_without_auth(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
