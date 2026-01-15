from __future__ import annotations

import random
import time


class InputController:
    def __init__(self, delay_min_s: float, delay_max_s: float) -> None:
        self.delay_min_s = delay_min_s
        self.delay_max_s = delay_max_s

    def click_accept(self) -> None:
        delay = random.uniform(self.delay_min_s, self.delay_max_s)
        time.sleep(delay)
        # Placeholder for input automation. Replace with pyautogui/AutoIT.
        print(f"[automation] Would click Accept after {delay:.2f}s delay")

    def start_queue(self) -> None:
        print("[automation] Would click Find Match")

    def stop_queue(self) -> None:
        print("[automation] Would click Cancel Search")
