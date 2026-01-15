from __future__ import annotations

import logging
from threading import Thread

import requests
from PIL import Image, ImageDraw
import pystray

from config import load_config

logger = logging.getLogger(__name__)


def _icon_image() -> Image.Image:
    image = Image.new("RGB", (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")
    return image


def _toggle_auto_accept(icon: pystray.Icon) -> None:
    config = load_config()
    endpoint = f"http://{config.bind_host}:{config.bind_port}/toggle-auto-accept"
    payload = {"enabled": not config.auto_accept_enabled}
    headers = {"X-Auth-Token": config.auth_token}
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=2)
        response.raise_for_status()
        logger.info("Auto-accept toggled via tray.")
    except requests.RequestException as exc:
        logger.error("Failed to toggle auto-accept: %s", exc)


def _quit(icon: pystray.Icon) -> None:
    icon.stop()


def main() -> None:
    menu = pystray.Menu(
        pystray.MenuItem("Toggle Auto-Accept", lambda icon, _: _toggle_auto_accept(icon)),
        pystray.MenuItem("Quit", lambda icon, _: _quit(icon)),
    )
    icon = pystray.Icon("dota-auto-accept", _icon_image(), "Dota Auto Accept", menu)
    thread = Thread(target=icon.run, daemon=True)
    thread.start()
    thread.join()


if __name__ == "__main__":
    main()
