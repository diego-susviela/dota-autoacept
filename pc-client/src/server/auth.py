from __future__ import annotations

from fastapi import HTTPException, Request, status


def require_token(request: Request, expected_token: str) -> None:
    provided = request.headers.get("X-Auth-Token")
    if not provided or provided != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing auth token.",
        )
