from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import RequestReplyProtocol


class AdminClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port

    def call(self, method: str, **kwargs) -> str:
        request = RequestReplyProtocol.build_request(
            "MatchService",
            method,
            kwargs,
        )
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(request.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8")
        print(f"Requisição enviada: {request}")
        print(f"Resposta do servidor: {response}")
        return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente administrativo do sistema de eventos esportivos.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor.")
    parser.add_argument("--action", choices=["goal", "card", "score", "events", "end"], required=True)
    parser.add_argument("--team", type=str, default="Flamengo")
    parser.add_argument("--player", type=str, default="Pedro")
    parser.add_argument("--minute", type=str, default="13'")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    client = AdminClient(host=args.host, port=args.port)
    if args.action == "goal":
        client.call("register_goal", team=args.team, player=args.player, minute=args.minute)
    elif args.action == "card":
        client.call("register_card", team=args.team, player=args.player, minute=args.minute)
    elif args.action == "score":
        client.call("get_score")
    elif args.action == "events":
        client.call("get_events")
    elif args.action == "end":
        client.call("end_match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
