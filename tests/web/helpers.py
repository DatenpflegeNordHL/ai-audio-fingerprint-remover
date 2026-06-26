from __future__ import annotations

import asyncio
from dataclasses import dataclass
import base64
import io
import json
from pathlib import Path
import wave

from audio_quality_humanizer.web.app import create_app


@dataclass
class AsgiResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict:
        return json.loads(self.body.decode("utf-8"))


def tiny_wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b"\x00\x00" * 8)
    return buffer.getvalue()


def multipart_body(
    *,
    mode: str = "analyze",
    filename: str = "input.wav",
    content: bytes | None = None,
    content_type: str = "audio/wav",
) -> tuple[bytes, str]:
    boundary = "aqh-test-boundary"
    content = tiny_wav_bytes() if content is None else content
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="mode"\r\n\r\n'
        f"{mode}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    body += content
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, f"multipart/form-data; boundary={boundary}"


def multipart_two_file_body(
    *,
    mode: str = "compare",
    before_filename: str = "before.wav",
    after_filename: str = "after.wav",
    before_content: bytes | None = None,
    after_content: bytes | None = None,
    content_type: str = "audio/wav",
) -> tuple[bytes, str]:
    boundary = "aqh-test-boundary"
    before_content = tiny_wav_bytes() if before_content is None else before_content
    after_content = tiny_wav_bytes() if after_content is None else after_content
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="mode"\r\n\r\n'
        f"{mode}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="before_file"; filename="{before_filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    body += before_content
    body += (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="after_file"; filename="{after_filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    body += after_content
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, f"multipart/form-data; boundary={boundary}"


def auth_header(token: str = "test-token") -> dict[str, str]:
    return {"authorization": f"Bearer {token}"}


def basic_auth_header(username: str = "beta", password: str = "secret") -> dict[str, str]:
    encoded = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"authorization": f"Basic {encoded}"}


def call_app(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
) -> AsgiResponse:
    return asyncio.run(_call_app(method, path, headers=headers, body=body))


async def _call_app(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None,
    body: bytes,
) -> AsgiResponse:
    app = create_app()
    encoded_headers = [
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method.upper(),
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": encoded_headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    messages: list[dict] = []
    request_sent = False

    async def receive() -> dict:
        nonlocal request_sent
        if request_sent:
            return {"type": "http.disconnect"}
        request_sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict) -> None:
        messages.append(message)

    await app(scope, receive, send)

    status_code = 500
    response_headers: dict[str, str] = {}
    chunks: list[bytes] = []
    for message in messages:
        if message["type"] == "http.response.start":
            status_code = message["status"]
            response_headers = {
                key.decode("latin-1"): value.decode("latin-1")
                for key, value in message.get("headers", [])
            }
        elif message["type"] == "http.response.body":
            chunks.append(message.get("body", b""))
    return AsgiResponse(status_code=status_code, headers=response_headers, body=b"".join(chunks))


def prepare_env(monkeypatch, tmp_path: Path, *, token: str = "test-token", max_upload_mib: int = 100) -> Path:
    job_root = tmp_path / "jobs"
    monkeypatch.setenv("AQH_WEB_TOKEN", token)
    monkeypatch.setenv("AQH_WEB_JOB_ROOT", str(job_root))
    monkeypatch.setenv("AQH_MAX_UPLOAD_MIB", str(max_upload_mib))
    monkeypatch.setenv("AQH_JOB_TTL_HOURS", "24")
    monkeypatch.setenv("AQH_PARTIAL_TTL_MINUTES", "60")
    monkeypatch.delenv("AQH_WEB_JOBS_DIR", raising=False)
    monkeypatch.delenv("AQH_WEB_MAX_UPLOAD_MB", raising=False)
    monkeypatch.delenv("AQH_WEB_JOB_TTL_HOURS", raising=False)
    monkeypatch.delenv("AQH_BETA_PASSWORD", raising=False)
    monkeypatch.delenv("AQH_BETA_PASSWORD_HASH", raising=False)
    return job_root
