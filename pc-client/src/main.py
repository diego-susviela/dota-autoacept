from __future__ import annotations

import json
from pathlib import Path

import uvicorn

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def main() -> None:
    config = load_config()
    uvicorn.run(
        "server.app:app",
        host=config["bind_host"],
        port=config["bind_port"],
        reload=False,
    )


if __name__ == "__main__":
    main()
