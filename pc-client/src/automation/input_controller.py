from __future__ import annotations

import random
import time

import pyautogui

from server.config import Region


class InputController:
    def __init__(
        self,
        delay_min_s: float,
        delay_max_s: float,
        jitter_px: int,
        cooldown_s: float,
    ) -> None:
        self.delay_min_s = delay_min_s
        self.delay_max_s = delay_max_s
        self.jitter_px = jitter_px
        self.cooldown_s = cooldown_s
        self._last_click_at = 0.0

    def click_accept(self, region: Region) -> None:
        if not self._region_configured(region):
            return
        delay = random.uniform(self.delay_min_s, self.delay_max_s)
        time.sleep(delay)
        x, y = self._jittered_center(region)
        self._click(x, y)

    def start_queue(self, region: Region) -> None:
        if not self._region_configured(region):
            return
        x, y = self._jittered_center(region)
        self._click(x, y)

    def stop_queue(self, region: Region) -> None:
        if not self._region_configured(region):
            return
        x, y = self._jittered_center(region)
        self._click(x, y)

    def _region_configured(self, region: Region) -> bool:
        return region.width > 0 and region.height > 0

    def _jittered_center(self, region: Region) -> tuple[int, int]:
        center_x = region.x + region.width // 2
        center_y = region.y + region.height // 2
        jitter_x = random.randint(-self.jitter_px, self.jitter_px)
        jitter_y = random.randint(-self.jitter_px, self.jitter_px)
        return center_x + jitter_x, center_y + jitter_y

    def _click(self, x: int, y: int) -> None:
        now = time.monotonic()
        if now - self._last_click_at < self.cooldown_s:
            return
        self._last_click_at = now
        pyautogui.click(x=x, y=y)
