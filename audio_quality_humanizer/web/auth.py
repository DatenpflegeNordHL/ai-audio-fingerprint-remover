"""Bearer-token authentication for the optional private web backend."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from audio_quality_humanizer.web.config import WebConfig, load_config


bearer_scheme = HTTPBearer(auto_error=False)


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
