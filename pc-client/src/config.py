from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"


class Region(BaseModel):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class AcceptColor(BaseModel):
    r: int = 255
    g: int = 255
    b: int = 255
    tolerance: int = 25


class AppConfig(BaseModel):
    bind_host: str = "127.0.0.1"
    bind_port: int = 8765
    auth_token: str = "change-me"
    auto_accept_enabled: bool = True
    accept_delay_min_s: float = 0.2
    accept_delay_max_s: float = 0.5
    click_cooldown_s: float = 5.0
    poll_interval_s: float = 0.5
    enable_ocr: bool = False
    ocr_text: str = "ACCEPT"
    accept_region: Region = Field(default_factory=Region)
    queue_region: Region = Field(default_factory=Region)
    accept_color: AcceptColor = Field(default_factory=AcceptColor)
    log_path: str = "logs/pc-client.log"
    log_level: str = "INFO"
    stop_after_match_found_s: float = 8.0
    allowed_subnets: list[str] = Field(
        default_factory=lambda: [
            "127.0.0.1/32",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
        ]
    )


class ConfigError(RuntimeError):
    pass


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    raw = json.loads(path.read_text())
    try:
        return AppConfig(**raw)
    except ValidationError as exc:
        raise ConfigError(str(exc)) from exc


def save_config(config: AppConfig, path: Path = CONFIG_PATH) -> None:
    path.write_text(json.dumps(config.model_dump(), indent=2))


def update_config(updates: dict[str, Any], path: Path = CONFIG_PATH) -> AppConfig:
    current = json.loads(path.read_text())
    current.update(updates)
    path.write_text(json.dumps(current, indent=2))
    return load_config(path)
