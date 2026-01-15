from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass

import pyautogui

logger = logging.getLogger(__name__)


@dataclass
class ClickRegion:
    x: int
    y: int
    width: int
    height: int

    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


class InputController:
    def __init__(self, delay_min_s: float, delay_max_s: float, cooldown_s: float) -> None:
        self.delay_min_s = delay_min_s
        self.delay_max_s = delay_max_s
        self.cooldown_s = cooldown_s
        self._last_click_at = 0.0

    def _human_delay(self) -> None:
        delay = random.uniform(self.delay_min_s, self.delay_max_s)
        time.sleep(delay)

    def _can_click(self) -> bool:
        return (time.time() - self._last_click_at) >= self.cooldown_s

    def _click_region(self, region: ClickRegion) -> None:
        if region.width <= 0 or region.height <= 0:
            logger.warning("Click region not configured; skipping click.")
            return
        if not self._can_click():
            logger.info("Click suppressed by cooldown.")
            return
        self._human_delay()
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)
        target_x, target_y = region.center()
        pyautogui.click(target_x + jitter_x, target_y + jitter_y)
        self._last_click_at = time.time()

    def click_accept(self, region: ClickRegion) -> None:
        logger.info("Clicking Accept button.")
        self._click_region(region)

    def start_queue(self, region: ClickRegion) -> None:
        logger.info("Clicking Find Match button.")
        self._click_region(region)

    def stop_queue(self, region: ClickRegion) -> None:
        logger.info("Clicking Cancel Search button.")
        self._click_region(region)
