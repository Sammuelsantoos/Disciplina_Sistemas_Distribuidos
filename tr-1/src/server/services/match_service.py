"""Serviço thread-safe que mantém partidas e seus eventos em memória."""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Dict, List

from src.shared.models import Match, MatchEvent


class MatchService:
    """Gerencia o placar e o histórico de eventos das partidas cadastradas."""

    VALID_EVENT_TYPES = {"GOL", "CARD", "END"}

    def __init__(self):
        self._matches: Dict[int, Match] = {}
        self._events: Dict[int, List[MatchEvent]] = defaultdict(list)
        self._event_ids = set()
        self._lock = threading.RLock()

    def create_match(self, match_id: int, home_team: str, away_team: str) -> Match:
        """Cadastra uma partida ainda não existente, iniciando o placar em zero."""
        try:
            normalized_id = int(match_id)
        except (TypeError, ValueError) as error:
            raise ValueError("match_id deve ser um número inteiro.") from error

        home = self._validate_team(home_team, "home_team")
        away = self._validate_team(away_team, "away_team")
        if home.casefold() == away.casefold():
            raise ValueError("Os times mandante e visitante devem ser diferentes.")

        with self._lock:
            if normalized_id in self._matches:
                raise ValueError(f"Partida {normalized_id} já está cadastrada.")
            match = Match(normalized_id, home, away)
            self._matches[normalized_id] = match
            return match

    def register_event(
        self,
        event_id: int,
        match_id: int,
        event_type: str,
        description: str,
        team: str | None = None,
    ) -> MatchEvent:
        """Registra um evento e atualiza o placar quando o evento é um gol."""
        try:
            normalized_event_id = int(event_id)
            normalized_match_id = int(match_id)
        except (TypeError, ValueError) as error:
            raise ValueError("event_id e match_id devem ser números inteiros.") from error

        normalized_type = str(event_type or "").upper()
        if normalized_type not in self.VALID_EVENT_TYPES:
            valid = ", ".join(sorted(self.VALID_EVENT_TYPES))
            raise ValueError(f"Tipo de evento inválido. Use: {valid}.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("A descrição do evento é obrigatória.")

        with self._lock:
            match = self._matches.get(normalized_match_id)
            if match is None:
                raise KeyError(f"Partida {normalized_match_id} não encontrada.")
            if normalized_event_id in self._event_ids:
                raise ValueError(f"Evento {normalized_event_id} já está cadastrado.")

            if normalized_type == "GOL":
                side = self._team_side(match, team)
                if side == "home":
                    match.home_score += 1
                else:
                    match.away_score += 1

            event = MatchEvent(
                normalized_event_id, normalized_match_id, normalized_type, description.strip()
            )
            self._events[normalized_match_id].append(event)
            self._event_ids.add(normalized_event_id)
            return event

    def get_match(self, match_id: int) -> Match:
        """Retorna a partida solicitada ou levanta ``KeyError`` se não existir."""
        try:
            normalized_id = int(match_id)
        except (TypeError, ValueError) as error:
            raise ValueError("match_id deve ser um número inteiro.") from error
        with self._lock:
            match = self._matches.get(normalized_id)
            if match is None:
                raise KeyError(f"Partida {normalized_id} não encontrada.")
            return match

    def get_events(self, match_id: int) -> List[MatchEvent]:
        """Retorna uma cópia do histórico de eventos da partida."""
        self.get_match(match_id)
        with self._lock:
            return list(self._events[int(match_id)])

    @staticmethod
    def _validate_team(team: str, field: str) -> str:
        if not isinstance(team, str) or not team.strip():
            raise ValueError(f"{field} é obrigatório.")
        return team.strip()

    @staticmethod
    def _team_side(match: Match, team: str | None) -> str:
        if not isinstance(team, str) or not team.strip():
            raise ValueError("Informe o time que marcou o gol.")
        normalized_team = team.strip().casefold()
        if normalized_team == match.home_team.casefold():
            return "home"
        if normalized_team == match.away_team.casefold():
            return "away"
        raise ValueError(f"O time '{team}' não participa da partida {match.match_id}.")
