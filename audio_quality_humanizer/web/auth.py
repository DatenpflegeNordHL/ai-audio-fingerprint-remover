"""Bearer-token authentication for the optional private web backend."""

from __future__ import annotations

import hashlib
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials, HTTPBearer

from audio_quality_humanizer.web.config import WebConfig, load_config


bearer_scheme = HTTPBearer(auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)


def require_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> WebConfig:
    """Require the configured private-beta bearer token."""

    config = load_config()
    if not config.token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Private web API bearer token is not configured.",
        )
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required for private beta API access.",
        )
    if not secrets.compare_digest(credentials.credentials, config.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token was not accepted for private beta API access.",
        )
    return config


def require_beta_dashboard_access(
    credentials: HTTPBasicCredentials | None = Depends(basic_scheme),
) -> WebConfig:
    """Optionally require a temporary shared beta password for the dashboard."""

    config = load_config()
    if not config.beta_password and not config.beta_password_hash:
        return config
    if credentials is None or credentials.username != "beta":
        raise _beta_auth_error()
    if config.beta_password_hash:
        accepted = _verify_beta_password_hash(credentials.password, config.beta_password_hash)
    else:
        accepted = secrets.compare_digest(credentials.password, config.beta_password or "")
    if not accepted:
        raise _beta_auth_error()
    return config


def _beta_auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Private beta dashboard password required.",
        headers={"WWW-Authenticate": 'Basic realm="audio-quality-humanizer-private-beta"'},
    )


def _verify_beta_password_hash(password: str, configured_hash: str) -> bool:
    if configured_hash.startswith("sha256:"):
        expected = configured_hash.removeprefix("sha256:")
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return secrets.compare_digest(digest, expected)
    if configured_hash.startswith("pbkdf2_sha256$"):
        return _verify_pbkdf2_sha256(password, configured_hash)
    return False


def _verify_pbkdf2_sha256(password: str, configured_hash: str) -> bool:
    try:
        _algorithm, iterations, salt_hex, digest_hex = configured_hash.split("$", 3)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    except (ValueError, TypeError):
        return False
    return secrets.compare_digest(derived, expected)
