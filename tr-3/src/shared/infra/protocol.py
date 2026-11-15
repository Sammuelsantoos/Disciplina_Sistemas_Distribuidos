"""Protocolo simples de requisição-resposta para chamadas RPC em Python."""

from __future__ import annotations

import json
from typing import Any


class RequestReplyProtocol:
    """Encapsula a representação em JSON de uma chamada remota."""

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
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("Payload inválido para chamada RPC.") from exc

        return {
            "message_type": data.get("messageType", "REQUEST"),
            "request_id": data.get("requestId", 1),
            "object_reference": data.get("objectReference", "MatchService"),
            "method_id": data.get("methodId", ""),
            "arguments": data.get("arguments", {}),
        }

    @staticmethod
    def build_reply(
        request_id: int,
        success: bool,
        result: Any = None,
        error: str | None = None,
    ) -> str:
        payload = {
            "messageType": "REPLY",
            "requestId": request_id,
            "success": success,
            "result": result,
            "error": error,
        }
        return json.dumps(payload, ensure_ascii=False)


def build_request(method: str, *args: str) -> str:
    """Compatibilidade com a versão mínima anterior do protocolo."""
    if not args:
        return f"{method}:"
    return f"{method}:{':'.join(args)}"


def parse_request(payload: str) -> tuple[str, str]:
    """Compatibilidade com a versão mínima anterior do protocolo."""
    method, separator, argument = payload.partition(":")
    if not separator:
        raise ValueError("Payload inválido para chamada RPC.")
    return method, argument
