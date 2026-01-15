from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel, Field, field_validator, model_validator


def resolve_config_path() -> Path:
    env_path = Path("config.json")
    if "PC_CLIENT_CONFIG" in os.environ:
        env_path = Path(os.environ["PC_CLIENT_CONFIG"])
    return env_path


class Region(BaseModel):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class PixelProbe(BaseModel):
    r: int = 0
    g: int = 200
    b: int = 0
    tolerance: int = 40


class AppConfig(BaseModel):
    bind_host: str = "127.0.0.1"
    bind_port: int = 8765
    auth_token: str = "change-me"
    auto_accept_enabled: bool = True
    accept_delay_min_s: float = 0.2
    accept_delay_max_s: float = 0.5
    accept_click_jitter_px: int = 4
    accept_click_cooldown_s: float = 1.0
    stop_after_match_found_s: float = 15.0
    accept_region: Region = Field(default_factory=Region)
    queue_region: Region = Field(default_factory=Region)
    accept_pixel_probe: PixelProbe = Field(default_factory=PixelProbe)
    poll_interval_s: float = 0.75
    allowed_subnets: List[str] = Field(
        default_factory=lambda: ["127.0.0.1/32", "192.168.0.0/16", "10.0.0.0/8"]
    )
    log_file: str = "pc-client.log"

    @field_validator("bind_port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if value <= 0 or value >= 65536:
            raise ValueError("bind_port must be a valid TCP port")
        return value

    @model_validator(mode="after")
    def validate_delays(self) -> "AppConfig":
        if self.accept_delay_min_s > self.accept_delay_max_s:
            raise ValueError("accept_delay_min_s must be <= accept_delay_max_s")
        return self

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or resolve_config_path()
    if not config_path.exists():
        config = AppConfig()
        config_path.write_text(config.to_json())
        return config
    data: Any = json.loads(config_path.read_text())
    return AppConfig.model_validate(data)


def save_config(config: AppConfig, path: Path | None = None) -> None:
    config_path = path or resolve_config_path()
    config_path.write_text(config.to_json())
