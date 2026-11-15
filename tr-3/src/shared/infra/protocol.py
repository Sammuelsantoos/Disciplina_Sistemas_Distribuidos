"""Protocolo para arquitetura publicar e assinar em Python."""

from __future__ import annotations

import json
from typing import Any


class EventProtocol:
    """Mensagem de eventos para canal de publicação."""

    @staticmethod
    def build_publish(topic: str, payload: dict[str, Any]) -> str:
        message = {"action": "PUBLISH", "topic": topic, "payload": payload}
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def build_subscribe(topic: str, subscriber_id: str = "client") -> str:
        message = {"action": "SUBSCRIBE", "topic": topic, "subscriber_id": subscriber_id}
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def build_ack(topic: str, status: str, payload: Any = None) -> str:
        message = {"action": "ACK", "topic": topic, "status": status, "payload": payload}
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def build_query(query: str, topic: str = "match.events") -> str:
        message = {"action": "QUERY", "topic": topic, "query": query}
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def build_notify(topic: str, payload: dict[str, Any]) -> str:
        message = {"action": "NOTIFY", "topic": topic, "payload": payload}
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def parse_message(raw_message: str) -> dict[str, Any]:
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError as exc:
            raise ValueError("Mensagem inválida para o broker de eventos.") from exc
        return data


class RequestReplyProtocol:
    """Mantém compatibilidade com a camada anterior do projeto."""

    @staticmethod
    def build_request(
        object_reference: str,
        method_id: str,
        arguments: dict[str, Any] | None = None,
        request_id: int = 1,
        message_type: str = "REQUEST",
    ) -> str:
        payload = {
            "messageType": message_type,
            "requestId": request_id,
            "objectReference": object_reference,
            "methodId": method_id,
            "arguments": arguments or {},
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def parse_request(payload: str) -> dict[str, Any]:
        data = json.loads(payload)
        return {
            "message_type": data.get("messageType", "REQUEST"),
            "request_id": data.get("requestId", 1),
            "object_reference": data.get("objectReference", "MatchService"),
            "method_id": data.get("methodId", ""),
            "arguments": data.get("arguments", {}),
        }

    @staticmethod
    def build_reply(request_id: int, success: bool, result: Any = None, error: str | None = None) -> str:
        payload = {
            "messageType": "REPLY",
            "requestId": request_id,
            "success": success,
            "result": result,
            "error": error,
        }
        return json.dumps(payload, ensure_ascii=False)


def build_request(method: str, *args: str) -> str:
    return f"{method}:{':'.join(args)}" if args else f"{method}:"


def parse_request(payload: str) -> tuple[str, str]:
    method, separator, argument = payload.partition(":")
    if not separator:
        raise ValueError("Payload inválido para chamada RPC.")
    return method, argument
