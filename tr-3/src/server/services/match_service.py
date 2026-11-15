from __future__ import annotations

from src.shared.models.match import Match
from src.shared.models.match_event import MatchEvent


class MatchService:
    def __init__(self, home_team: str = "Flamengo", away_team: str = "Vasco") -> None:
        self.match = Match(home_team=home_team, away_team=away_team)

    def register_goal(self, team: str, player: str, minute: str) -> dict:
        event_id = len(self.match.events) + 1
        description = f"{player} marcou para {team} aos {minute}."
        event = MatchEvent(
            event_id=event_id,
            event_type="gol",
            description=description,
            minute=minute,
            team=team,
            player=player,
        )
        self.match.add_event(event)

        if team == self.match.home_team:
            self.match.home_score += 1
        elif team == self.match.away_team:
            self.match.away_score += 1

        return {
            "event_type": "gol",
            "team": team,
            "player": player,
            "minute": minute,
            "home_score": self.match.home_score,
            "away_score": self.match.away_score,
            "description": description,
        }

    def register_card(self, team: str, player: str, minute: str) -> dict:
        event_id = len(self.match.events) + 1
        description = f"Cartão para {player} do {team} aos {minute}."
        event = MatchEvent(
            event_id=event_id,
            event_type="cartao",
            description=description,
            minute=minute,
            team=team,
            player=player,
        )
        self.match.add_event(event)

        return {
            "event_type": "cartao",
            "team": team,
            "player": player,
            "minute": minute,
            "home_score": self.match.home_score,
            "away_score": self.match.away_score,
            "description": description,
        }

    def get_score(self) -> dict:
        return {
            "home_team": self.match.home_team,
            "away_team": self.match.away_team,
            "home_score": self.match.home_score,
            "away_score": self.match.away_score,
        }

    def get_events(self) -> list[dict]:
        return [event.to_dict() for event in self.match.events]

    def end_match(self) -> dict:
        return {
            "status": "encerrado",
            "home_score": self.match.home_score,
            "away_score": self.match.away_score,
        }
