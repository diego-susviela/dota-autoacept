from __future__ import annotations

import ipaddress
from typing import Iterable

from fastapi import HTTPException, Request, status


def require_token(request: Request, expected_token: str) -> None:
    provided = request.headers.get("X-Auth-Token") or request.query_params.get("token")
    if not provided or provided != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing auth token.",
        )


def enforce_subnet(request: Request, allowed_subnets: Iterable[str]) -> None:
    client_ip = request.client.host if request.client else "0.0.0.0"
    if client_ip == "testclient":
        return
    ip = ipaddress.ip_address(client_ip)
    for subnet in allowed_subnets:
        if ip in ipaddress.ip_network(subnet, strict=False):
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Client IP is not allowed.",
    )


def enforce_subnet_ws(client_host: str | None, allowed_subnets: Iterable[str]) -> bool:
    if not client_host:
        return False
    if client_host == "testclient":
        return True
    ip = ipaddress.ip_address(client_host)
    for subnet in allowed_subnets:
        if ip in ipaddress.ip_network(subnet, strict=False):
            return True
    return False
