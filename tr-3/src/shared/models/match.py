from __future__ import annotations

from dataclasses import dataclass, field

from src.shared.models.match_event import MatchEvent


@dataclass
class Match:
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    events: list[MatchEvent] = field(default_factory=list)

    def add_event(self, event: MatchEvent) -> None:
        self.events.append(event)

    def to_dict(self) -> dict:
        return {
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "events": [event.to_dict() for event in self.events],
        }
