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
    assert response.json()["status"] == "uploaded"
