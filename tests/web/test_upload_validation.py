from __future__ import annotations

from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env, tiny_wav_bytes


def _post_upload(tmp_path, monkeypatch, *, filename: str, content: bytes | None = None, max_upload_mib: int = 100):
    prepare_env(monkeypatch, tmp_path, max_upload_mib=max_upload_mib)
    body, content_type = multipart_body(filename=filename, content=content)
    return call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )


def test_valid_tiny_wav_upload_is_accepted(tmp_path, monkeypatch):
    response = _post_upload(tmp_path, monkeypatch, filename="input.wav")

    assert response.status_code == 201
    data = response.json()
    assert data["mode"] == "analyze"
    assert data["status"] == "completed"
    assert data["input"]["extension"] == ".wav"
    assert data["input"]["size_bytes"] == len(tiny_wav_bytes())


def test_uppercase_valid_extension_is_accepted(tmp_path, monkeypatch):
    response = _post_upload(tmp_path, monkeypatch, filename="INPUT.WAV")

    assert response.status_code == 201
    assert response.json()["input"]["extension"] == ".wav"


def test_disallowed_extensions_are_rejected(tmp_path, monkeypatch):
    for filename in ("input.txt", "input.exe", "input.zip"):
        response = _post_upload(tmp_path, monkeypatch, filename=filename)
        assert response.status_code == 400


def test_missing_extension_is_rejected(tmp_path, monkeypatch):
    response = _post_upload(tmp_path, monkeypatch, filename="input")

    assert response.status_code == 400


def test_empty_file_is_rejected(tmp_path, monkeypatch):
    response = _post_upload(tmp_path, monkeypatch, filename="input.wav", content=b"")

    assert response.status_code == 400


def test_oversize_upload_is_rejected_with_413(tmp_path, monkeypatch):
    content = tiny_wav_bytes() + (b"\x00" * (1024 * 1024))
    response = _post_upload(tmp_path, monkeypatch, filename="input.wav", content=content, max_upload_mib=1)

    assert response.status_code == 413


def test_unrecognized_magic_bytes_are_rejected(tmp_path, monkeypatch):
    response = _post_upload(tmp_path, monkeypatch, filename="input.wav", content=b"not a wav")

    assert response.status_code == 400
