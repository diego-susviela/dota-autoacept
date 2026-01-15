from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

from server.state import QueueState


@dataclass
class DetectorConfig:
    poll_interval_s: float = 1.0


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
        """
        Placeholder detection loop.

        Replace this with pixel/OCR/audio detection logic. It should
        only use visible cues and must stop once a match starts.
        """
        self._running = True
        while self._running:
            await asyncio.sleep(self._config.poll_interval_s)

    def stop(self) -> None:
        self._running = False
