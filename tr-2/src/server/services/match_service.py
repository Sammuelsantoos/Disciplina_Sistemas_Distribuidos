"""Serviço thread-safe que mantém partidas e seus eventos em memória."""

from __future__ import annotations

import os
import threading
from collections import defaultdict
from typing import Dict, List

from src.shared.models import Match, MatchEvent, GoalEvent, CardEvent
from src.shared.streams import MatchEventInputStream
from src.shared.streams import MatchEventOutputStream


class MatchService:
    """Gerencia o placar e o histórico de eventos das partidas cadastradas."""

    VALID_EVENT_TYPES = {"GOL", "CARD", "END"}

    def __init__(self, storage_path: str = "src/data/event.csv"):
        """Inicializa o serviço e carrega os eventos históricos armazenados."""
        self._matches: Dict[int, Match] = {}
        self._events: Dict[int, List[MatchEvent]] = defaultdict(list)
        self._event_ids = set()
        self._lock = threading.RLock()
        self._storage_path = storage_path

        if os.path.exists(self._storage_path):
            try:
                with open(self._storage_path, "r", encoding="utf-8") as file:
                    input_stream = MatchEventInputStream(source_stream=file)
                    saved_events = input_stream.read_all()
                    for event in saved_events:
                        self._reload_historical_event(event)
            except (OSError, ValueError, TypeError):
                pass

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
        """Registra um evento e updates o placar quando o evento é um gol."""
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

            event = self._factory_event(
                event_id=normalized_event_id,
                match_id=normalized_match_id,
                event_type=normalized_type,
                description=description.strip(),
                context_value=team
            )

            self._events[normalized_match_id].append(event)
            self._event_ids.add(normalized_event_id)

            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            with open(self._storage_path, "a", encoding="utf-8") as file:
                output_stream = MatchEventOutputStream(
                    destination_stream=file, event_array=[event], count=1
                )
                output_stream.write_all()

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

    def _reload_historical_event(self, event: MatchEvent) -> None:
        """Recarrega um evento do armazenamento local para a estrutura em memória."""
        with self._lock:
            if event.match_id not in self._matches:
                self._matches[event.match_id] = Match(
                    event.match_id, "Desconhecido", "Desconhecido"
                )

            match = self._matches[event.match_id]

            historical_team = getattr(event, "team", None) or getattr(event, "player", None)
            rich_event = self._factory_event(
                event_id=event.event_id,
                match_id=event.match_id,
                event_type=event.event_type,
                description=event.description,
                timestamp=event.timestamp,
                context_value=historical_team
            )

            self._events[rich_event.match_id].append(rich_event)
            self._event_ids.add(rich_event.event_id)

            if str(rich_event.event_type).upper() == "GOL":
                try:
                    side = self._team_side(match, getattr(rich_event, "team", None))
                    if side == "home":
                        match.home_score += 1
                    else:
                        match.away_score += 1
                except ValueError:
                    match.home_score += 1

    def _factory_event(
        self,
        event_id: int,
        match_id: int,
        event_type: str,
        description: str,
        timestamp: int | None = None,
        context_value: str | None = None
    ) -> MatchEvent:
        """Cria e retorna a instância específica de subclasse com base no tipo de evento."""
        if event_type == "GOL":
            return GoalEvent(
                event_id=event_id,
                match_id=match_id,
                team=context_value or "Desconhecido",
                description=description,
                timestamp=timestamp
            )
        if event_type == "CARD":
            return CardEvent(
                event_id=event_id,
                match_id=match_id,
                player=context_value or "Jogador Desconhecido",
                description=description,
                timestamp=timestamp
            )
        return MatchEvent(
            event_id=event_id,
            match_id=match_id,
            event_type=event_type,
            description=description,
            timestamp=timestamp
        )

    @staticmethod
    def _validate_team(team: str, field: str) -> str:
        """Valida se o nome do time enviado é uma string válida e preenchida."""
        if not isinstance(team, str) or not team.strip():
            raise ValueError(f"{field} é obrigatório.")
        return team.strip()

    @staticmethod
    def _team_side(match: Match, team: str | None) -> str:
        """Identifica o lado (mandante ou visitante) do time associado ao gol."""
        if not isinstance(team, str) or not team.strip():
            raise ValueError("Informe o time que marcou o gol.")
        normalized_team = team.strip().casefold()
        if normalized_team == match.home_team.casefold():
            return "home"
        if normalized_team == match.away_team.casefold():
            return "away"
        raise ValueError(f"O time '{team}' não participa da partida {match.match_id}.")
