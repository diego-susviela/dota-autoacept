from __future__ import annotations

import uvicorn

from config import load_config


def main() -> None:
    config = load_config()
    uvicorn.run(
        "server.app:app",
        host=config.bind_host,
        port=config.bind_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
