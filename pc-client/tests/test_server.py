from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import config
from server.app import app


def _write_test_config(tmp_path: Path) -> Path:
    data = {
        "bind_host": "127.0.0.1",
        "bind_port": 8765,
        "auth_token": "test-token",
        "auto_accept_enabled": True,
        "accept_delay_min_s": 0.2,
        "accept_delay_max_s": 0.5,
        "click_cooldown_s": 1.0,
        "poll_interval_s": 0.5,
        "enable_ocr": False,
        "ocr_text": "ACCEPT",
        "accept_region": {"x": 0, "y": 0, "width": 0, "height": 0},
        "queue_region": {"x": 0, "y": 0, "width": 0, "height": 0},
        "accept_color": {"r": 255, "g": 255, "b": 255, "tolerance": 25},
        "log_path": str(tmp_path / "pc-client.log"),
        "log_level": "INFO",
        "stop_after_match_found_s": 5.0,
        "allowed_subnets": ["0.0.0.0/0"],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    return path


def test_status_endpoint(tmp_path, monkeypatch) -> None:
    config_path = _write_test_config(tmp_path)
    monkeypatch.setattr(config, "CONFIG_PATH", config_path)
    client = TestClient(app)
    response = client.get("/status", headers={"X-Auth-Token": "test-token"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["queue_state"] == "idle"


def test_toggle_auto_accept(tmp_path, monkeypatch) -> None:
    config_path = _write_test_config(tmp_path)
    monkeypatch.setattr(config, "CONFIG_PATH", config_path)
    client = TestClient(app)
    response = client.post(
        "/toggle-auto-accept",
        json={"enabled": False},
        headers={"X-Auth-Token": "test-token"},
    )
    assert response.status_code == 200
    assert response.json()["auto_accept_enabled"] is False
