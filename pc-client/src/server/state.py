from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class QueueState(str, Enum):
    idle = "idle"
    searching = "searching"
    match_found = "match_found"
    accepted = "accepted"


@dataclass
class AppState:
    queue_state: QueueState = QueueState.idle
    auto_accept_enabled: bool = True
    last_event: str | None = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, str | bool | None]:
        return {
            "queue_state": self.queue_state.value,
            "auto_accept_enabled": self.auto_accept_enabled,
            "last_event": self.last_event,
            **self.metadata,
        }
