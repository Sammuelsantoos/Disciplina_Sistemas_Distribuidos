from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MatchEvent:
    event_id: int
    event_type: str
    description: str
    minute: str
    team: str | None = None
    player: str | None = None

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "description": self.description,
            "minute": self.minute,
            "team": self.team,
            "player": self.player,
        }
