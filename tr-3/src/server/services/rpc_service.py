from __future__ import annotations

from src.server.services.match_service import MatchService
from src.shared.infra.protocol import RequestReplyProtocol


class RPCService:
    def __init__(self) -> None:
        self.match_service = MatchService()

    def dispatch(self, payload: str) -> str:
        parsed = RequestReplyProtocol.parse_request(payload)
        method_id = parsed["method_id"]
        arguments = parsed["arguments"] or {}

        if method_id == "register_goal":
            result = self.match_service.register_goal(
                arguments["team"],
                arguments["player"],
                arguments["minute"],
            )
            return RequestReplyProtocol.build_reply(parsed["request_id"], True, result)

        if method_id == "register_card":
            result = self.match_service.register_card(
                arguments["team"],
                arguments["player"],
                arguments["minute"],
            )
            return RequestReplyProtocol.build_reply(parsed["request_id"], True, result)

        if method_id == "get_score":
            result = self.match_service.get_score()
            return RequestReplyProtocol.build_reply(parsed["request_id"], True, result)

        if method_id == "get_events":
            result = self.match_service.get_events()
            return RequestReplyProtocol.build_reply(parsed["request_id"], True, result)

        if method_id == "end_match":
            result = self.match_service.end_match()
            return RequestReplyProtocol.build_reply(parsed["request_id"], True, result)

        return RequestReplyProtocol.build_reply(
            parsed["request_id"],
            False,
            error=f"Método não suportado: {method_id}",
        )
