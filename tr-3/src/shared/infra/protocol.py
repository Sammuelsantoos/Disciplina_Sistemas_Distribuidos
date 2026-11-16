"""Protocolo de serialização e comunicação para arquitetura Publicar/Assinar (Pub/Sub).

Este módulo define o formato das mensagens JSON trocadas entre Publishers,
Subscribers e o Broker de eventos esportivos via sockets TCP.
"""

from __future__ import annotations

import json
from typing import Any


class EventProtocol:
    """Serializador e parser de mensagens para o canal de eventos Pub/Sub."""

    @staticmethod
    def build_publish(topic: str, payload: dict[str, Any]) -> str:
        """Constrói uma mensagem JSON para publicar um evento em um tópico."""
        message = {"action": "PUBLISH", "topic": topic, "payload": payload}
        return json.dumps(message, ensure_ascii=False) + "\n"

    @staticmethod
    def build_subscribe(topic: str, subscriber_id: str = "client") -> str:
        """Constrói uma mensagem JSON para inscrever um cliente em um tópico."""
        message = {
            "action": "SUBSCRIBE",
            "topic": topic,
            "subscriber_id": subscriber_id,
        }
        return json.dumps(message, ensure_ascii=False) + "\n"

    @staticmethod
    def build_ack(topic: str, status: str, payload: Any = None) -> str:
        """Constrói uma resposta de confirmação (ACK) ou erro enviada pelo Broker."""
        message = {
            "action": "ACK",
            "topic": topic,
            "status": status,
            "payload": payload,
        }
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def build_query(
        query: str, topic: str = "match.events", match_id: int = 1
    ) -> str:
        """Constrói uma mensagem JSON para consultar placar, eventos ou partidas."""
        message = {
            "action": "QUERY",
            "topic": topic,
            "query": query,
            "match_id": match_id,
        }
        return json.dumps(message, ensure_ascii=False) + "\n"

    @staticmethod
    def build_notify(topic: str, payload: dict[str, Any]) -> str:
        """Constrói uma notificação push enviada pelo Broker aos assinantes."""
        message = {"action": "NOTIFY", "topic": topic, "payload": payload}
        return json.dumps(message, ensure_ascii=False) + "\n"

    @staticmethod
    def parse_message(raw_message: str) -> dict[str, Any]:
        """Converte uma string JSON recebida via socket em um dicionário validado."""
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError as exc:
            raise ValueError("Mensagem JSON inválida para o broker de eventos.") from exc

        if not isinstance(data, dict):
            raise ValueError("O payload da mensagem deve ser um objeto JSON (dict).")
        return data
