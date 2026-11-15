from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import EventProtocol


class AdminClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port

    def publish(self, topic: str, event: dict) -> str:
        request = EventProtocol.build_publish(topic, event)
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(request.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8")
        print(f"Evento publicado: {request}")
        print(f"Resposta do broker: {response}")
        return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente produtor em arquitetura publicar e assinar.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do broker.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do broker.")
    parser.add_argument("--action", choices=["goal", "card", "query-score", "query-events"], required=True)
    parser.add_argument("--topic", type=str, default="match.events")
    parser.add_argument("--team", type=str, default="Flamengo")
    parser.add_argument("--player", type=str, default="Pedro")
    parser.add_argument("--minute", type=str, default="13'")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    client = AdminClient(host=args.host, port=args.port)

    if args.action == "goal":
        client.publish(
            args.topic,
            {
                "event_type": "gol",
                "team": args.team,
                "player": args.player,
                "minute": args.minute,
                "description": f"{args.player} marcou para {args.team} aos {args.minute}.",
            },
        )
    elif args.action == "card":
        client.publish(
            args.topic,
            {
                "event_type": "cartao",
                "team": args.team,
                "player": args.player,
                "minute": args.minute,
                "description": f"Cartão para {args.player} do {args.team} aos {args.minute}.",
            },
        )
    elif args.action == "query-score":
        query = EventProtocol.build_query("score", topic="match.status")
        with socket.create_connection((args.host, args.port), timeout=5) as sock:
            sock.sendall(query.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8")
        print(response)
    elif args.action == "query-events":
        query = EventProtocol.build_query("events", topic="match.events")
        with socket.create_connection((args.host, args.port), timeout=5) as sock:
            sock.sendall(query.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8")
        print(response)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
