"""Módulo base do Broker de eventos para arquitetura Publicar/Assinar (Pub/Sub).

Este módulo fornece o gerenciamento de inscrições por tópico, armazenamento
de histórico em memória e distribuição de notificações para assinantes via socket
ou objetos locais.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any


class EventBroker:
    """Broker de eventos para arquitetura publicar e assinar (Pub/Sub)."""

    def __init__(self) -> None:
        """Inicializa os registros de assinantes por tópico e o histórico de mensagens."""
        self.subscriptions: dict[str, list[Any]] = defaultdict(list)
        self.history: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def subscribe(self, topic: str, subscriber: Any) -> bool:
        """Inscreve um cliente ou objeto ouvinte em um tópico específico."""
        if subscriber not in self.subscriptions[topic]:
            self.subscriptions[topic].append(subscriber)
        return True

    def unsubscribe(self, topic: str, subscriber: Any) -> None:
        """Remove a inscrição de um assinante de um tópico específico."""
        if topic in self.subscriptions:
            self.subscriptions[topic] = [
                sub for sub in self.subscriptions[topic] if sub is not subscriber
            ]

    def publish(self, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Registra a mensagem no histórico e notifica todos os assinantes do tópico."""
        message = {"topic": topic, "payload": payload}
        self.history[topic].append(message)

        for subscriber in list(self.subscriptions.get(topic, [])):
            if hasattr(subscriber, "sendall"):
                try:
                    notification = {
                        "action": "NOTIFY",
                        "topic": topic,
                        "payload": payload,
                    }
                    payload_json = json.dumps(notification, ensure_ascii=False) + "\n"
                    subscriber.sendall(payload_json.encode("utf-8"))
                except (OSError, TypeError):
                    self.unsubscribe(topic, subscriber)
            elif hasattr(subscriber, "receive"):
                subscriber.receive(message)

        return message
