from __future__ import annotations

import time

import pyautogui

from config import load_config, save_config


def prompt_position(label: str) -> tuple[int, int]:
    input(f"Move the mouse to the {label} corner and press Enter...")
    position = pyautogui.position()
    print(f"Captured {label} at {position}")
    return position.x, position.y


def capture_region(name: str) -> tuple[int, int, int, int]:
    print(f"Calibrating {name} region.")
    top_left = prompt_position(f"{name} top-left")
    bottom_right = prompt_position(f"{name} bottom-right")
    width = max(0, bottom_right[0] - top_left[0])
    height = max(0, bottom_right[1] - top_left[1])
    return top_left[0], top_left[1], width, height


def main() -> None:
    config = load_config()
    print("Starting calibration. You have 3 seconds to focus the Dota 2 window.")
    time.sleep(3)

    ax, ay, aw, ah = capture_region("Accept button")
    qx, qy, qw, qh = capture_region("Queue button (Find/Cancel)")

    config.accept_region.x = ax
    config.accept_region.y = ay
    config.accept_region.width = aw
    config.accept_region.height = ah

    config.queue_region.x = qx
    config.queue_region.y = qy
    config.queue_region.width = qw
    config.queue_region.height = qh

    save_config(config)
    print("Calibration saved to config.json")


if __name__ == "__main__":
    main()
