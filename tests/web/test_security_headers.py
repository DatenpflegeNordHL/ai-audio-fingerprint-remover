from __future__ import annotations

from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


def _assert_security_headers(response):
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-frame-options"] == "DENY"


def test_dashboard_has_security_headers(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/")

    assert response.status_code == 200
    _assert_security_headers(response)


def test_api_config_has_security_headers_and_no_store(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/api/config", headers=auth_header())

    assert response.status_code == 200
    _assert_security_headers(response)
    assert response.headers["cache-control"] == "no-store"


def test_artifact_response_has_security_headers_and_no_store(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="analyze")
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )
    job_id = upload.json()["job_id"]

    response = call_app("GET", f"/api/jobs/{job_id}/artifacts/analysis.json", headers=auth_header())

    assert response.status_code == 200
    _assert_security_headers(response)
    assert response.headers["cache-control"] == "no-store"
