from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from server.app import app
from server.config import AppConfig


def write_config(tmp_path: Path) -> Path:
    config = AppConfig()
    config.auth_token = "test-token"
    config.bind_host = "127.0.0.1"
    config.bind_port = 9999
    config.allowed_subnets = ["127.0.0.1/32"]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config.model_dump(), indent=2))
    return path


def test_status_endpoint(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    os.environ["PC_CLIENT_CONFIG"] = str(config_path)
    client = TestClient(app)
    response = client.get("/status", headers={"X-Auth-Token": "test-token"})
    assert response.status_code == 200
    body = response.json()
    assert "queue_state" in body


def test_toggle_auto_accept(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    os.environ["PC_CLIENT_CONFIG"] = str(config_path)
    client = TestClient(app)
    response = client.post(
        "/toggle-auto-accept",
        headers={"X-Auth-Token": "test-token"},
        json={"enabled": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["auto_accept_enabled"] is False
