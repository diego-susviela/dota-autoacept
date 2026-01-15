from __future__ import annotations

from dataclasses import asdict

import pyautogui

from server.config import Region, load_config, save_config


def capture_region(label: str) -> Region:
    input(f"Hover over the TOP-LEFT of the {label} and press Enter...")
    left, top = pyautogui.position()
    input(f"Hover over the BOTTOM-RIGHT of the {label} and press Enter...")
    right, bottom = pyautogui.position()
    width = max(0, right - left)
    height = max(0, bottom - top)
    return Region(x=left, y=top, width=width, height=height)


def main() -> None:
    config = load_config()
    config.accept_region = capture_region("Accept button")
    config.queue_region = capture_region("Queue button (Find/Cancel)")
    save_config(config)
    print("Calibration saved:")
    print(asdict(config.accept_region))
    print(asdict(config.queue_region))


if __name__ == "__main__":
    main()
