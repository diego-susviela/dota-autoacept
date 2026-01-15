from __future__ import annotations

import ipaddress
from fastapi import HTTPException, Request, status


def require_token(request: Request, expected_token: str, allowed_subnets: list[str]) -> None:
    provided = request.headers.get("X-Auth-Token")
    if not provided or provided != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing auth token.",
        )

    client_ip = request.client.host if request.client else ""
    if not _ip_allowed(client_ip, allowed_subnets):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client IP is not allowed.",
        )


def _ip_allowed(ip: str, allowed_subnets: list[str]) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for subnet in allowed_subnets:
        if address in ipaddress.ip_network(subnet):
            return True
    return False
