from __future__ import annotations

import json
from collections import defaultdict
from typing import Any


class EventBroker:
    """Broker de eventos para arquitetura publicar e assinar."""

    def __init__(self) -> None:
        self.subscriptions: dict[str, list[Any]] = defaultdict(list)
        self.history: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def subscribe(self, topic: str, subscriber: Any) -> bool:
        if subscriber not in self.subscriptions[topic]:
            self.subscriptions[topic].append(subscriber)
        return True

    def unsubscribe(self, topic: str, subscriber: Any) -> None:
        if topic in self.subscriptions:
            self.subscriptions[topic] = [s for s in self.subscriptions[topic] if s is not subscriber]

    def publish(self, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        message = {"topic": topic, "payload": payload}
        self.history[topic].append(message)

        for subscriber in list(self.subscriptions.get(topic, [])):
            if hasattr(subscriber, "sendall"):
                try:
                    payload_json = json.dumps({"action": "NOTIFY", "topic": topic, "payload": payload}, ensure_ascii=False)
                    subscriber.sendall(payload_json.encode("utf-8"))
                except Exception:
                    self.unsubscribe(topic, subscriber)
            elif hasattr(subscriber, "receive"):
                subscriber.receive(message)

        return message
