from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable

import pytesseract
from mss import mss
from PIL import Image

from server.state import QueueState

logger = logging.getLogger(__name__)


@dataclass
class DetectorConfig:
    poll_interval_s: float
    region: tuple[int, int, int, int]
    target_color: tuple[int, int, int]
    tolerance: int
    enable_ocr: bool
    ocr_text: str


class QueueDetector:
    def __init__(
        self,
        config: DetectorConfig,
        on_state_change: Callable[[QueueState], Awaitable[None]],
    ) -> None:
        self._config = config
        self._on_state_change = on_state_change
        self._running = False

    async def run(self) -> None:
        self._running = True
        if self._config.region[2] <= 0 or self._config.region[3] <= 0:
            logger.warning("Detection region not configured; detector idle.")
            return
        with mss() as screen:
            while self._running:
                if self._detect_accept(screen):
                    await self._on_state_change(QueueState.match_found)
                await asyncio.sleep(self._config.poll_interval_s)

    def stop(self) -> None:
        self._running = False

    def _detect_accept(self, screen: mss) -> bool:
        x, y, width, height = self._config.region
        monitor = {"top": y, "left": x, "width": width, "height": height}
        frame = screen.grab(monitor)
        image = Image.frombytes("RGB", frame.size, frame.rgb)
        pixels = list(image.getdata())
        if not pixels:
            return False
        avg = tuple(sum(channel) // len(pixels) for channel in zip(*pixels))
        if self._color_close(avg, self._config.target_color, self._config.tolerance):
            logger.info("Accept button detected via pixel sampling.")
            return True
        if self._config.enable_ocr:
            text = pytesseract.image_to_string(image).strip().upper()
            if self._config.ocr_text.upper() in text:
                logger.info("Accept button detected via OCR.")
                return True
        return False

    @staticmethod
    def _color_close(color: tuple[int, int, int], target: tuple[int, int, int], tolerance: int) -> bool:
        return all(abs(c - t) <= tolerance for c, t in zip(color, target))
