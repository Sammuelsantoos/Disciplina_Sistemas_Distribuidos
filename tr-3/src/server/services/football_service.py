"""Implementação do serviço de eventos de futebol em Python."""

from __future__ import annotations

from abc import ABC, abstractmethod


class FootballEventService(ABC):
    """Contrato do serviço disponibilizado pelo servidor."""

    @abstractmethod
    def publish_event(self, team: str, event_type: str, minute: str) -> str:
        """Retorna o resumo do evento do jogo."""


class FootballEventServiceImpl(FootballEventService):
    """Implementação concreta do serviço RPC de eventos de futebol."""

    def publish_event(self, team: str, event_type: str, minute: str) -> str:
        if event_type == "gol":
            return f"Evento de futebol: {team} marcou gol aos {minute}."
        if event_type == "cartao":
            return f"Evento de futebol: {team} recebeu cartão aos {minute}."
        if event_type == "substituicao":
            return f"Evento de futebol: {team} realizou substituição aos {minute}."
        return f"Evento de futebol: {team} teve ação {event_type} aos {minute}."
