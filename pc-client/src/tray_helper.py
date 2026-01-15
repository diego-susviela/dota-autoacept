from __future__ import annotations

import threading

import pystray
from PIL import Image, ImageDraw

from server.config import load_config, save_config


def create_icon() -> Image.Image:
    image = Image.new("RGB", (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(0, 200, 0))
    return image


def toggle_auto_accept(icon: pystray.Icon) -> None:
    config = load_config()
    config.auto_accept_enabled = not config.auto_accept_enabled
    save_config(config)
    icon.title = f"Auto-Accept: {'On' if config.auto_accept_enabled else 'Off'}"


def run_tray() -> None:
    icon = pystray.Icon("dota-autoaccept", create_icon())
    icon.title = "Auto-Accept: Unknown"
    icon.menu = pystray.Menu(
        pystray.MenuItem("Toggle Auto-Accept", lambda: toggle_auto_accept(icon)),
        pystray.MenuItem("Quit", lambda: icon.stop()),
    )
    icon.run()


def main() -> None:
    thread = threading.Thread(target=run_tray)
    thread.daemon = True
    thread.start()
    thread.join()


if __name__ == "__main__":
    main()
