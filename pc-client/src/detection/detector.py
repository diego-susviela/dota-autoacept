from __future__ import annotations

import asyncio
import importlib.util
from dataclasses import dataclass
from typing import Awaitable, Callable

import mss
from PIL import Image

from server.config import AppConfig, PixelProbe, Region
from server.state import QueueState


class QueueDetector:
    def __init__(
        self,
        config: AppConfig,
        on_state_change: Callable[[QueueState], Awaitable[None]],
    ) -> None:
        self._config = config
        self._on_state_change = on_state_change
        self._running = False
        self._last_state: QueueState | None = None
        self._ocr_available = importlib.util.find_spec("pytesseract") is not None

    async def run(self) -> None:
        self._running = True
        with mss.mss() as grabber:
            while self._running:
                detected_state = self._detect_state(grabber)
                if detected_state != self._last_state:
                    self._last_state = detected_state
                    await self._on_state_change(detected_state)
                await asyncio.sleep(self._config.poll_interval_s)

    def stop(self) -> None:
        self._running = False

    def _detect_state(self, grabber: mss.mss) -> QueueState:
        if self._match_found(grabber, self._config.accept_region, self._config.accept_pixel_probe):
            return QueueState.match_found
        return QueueState.searching if self._region_is_configured(self._config.queue_region) else QueueState.idle

    def _region_is_configured(self, region: Region) -> bool:
        return region.width > 0 and region.height > 0

    def _match_found(self, grabber: mss.mss, region: Region, probe: PixelProbe) -> bool:
        if not self._region_is_configured(region):
            return False
        sample = grabber.grab(
            {
                "left": region.x,
                "top": region.y,
                "width": region.width,
                "height": region.height,
            }
        )
        image = Image.frombytes("RGB", sample.size, sample.rgb)
        if self._pixel_probe_match(image, probe):
            return True
        if self._ocr_available:
            return self._ocr_match(image)
        return False

    def _pixel_probe_match(self, image: Image.Image, probe: PixelProbe) -> bool:
        width, height = image.size
        samples = [(width // 2, height // 2), (width // 4, height // 2), (3 * width // 4, height // 2)]
        for x, y in samples:
            r, g, b = image.getpixel((x, y))
            if (
                abs(r - probe.r) <= probe.tolerance
                and abs(g - probe.g) <= probe.tolerance
                and abs(b - probe.b) <= probe.tolerance
            ):
                return True
        return False

    def _ocr_match(self, image: Image.Image) -> bool:
        import pytesseract

        text = pytesseract.image_to_string(image).lower()
        return "accept" in text
