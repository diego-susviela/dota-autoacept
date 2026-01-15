from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    last_state_change_at: str | None = None
    last_match_found_at: str | None = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, str | bool | None]:
        return {
            "queue_state": self.queue_state.value,
            "auto_accept_enabled": self.auto_accept_enabled,
            "last_event": self.last_event,
            "last_state_change_at": self.last_state_change_at,
            "last_match_found_at": self.last_match_found_at,
            **self.metadata,
        }

    def set_state(self, new_state: QueueState, event: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.queue_state = new_state
        self.last_event = event
        self.last_state_change_at = now
        if new_state == QueueState.match_found:
            self.last_match_found_at = now
