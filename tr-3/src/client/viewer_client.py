from __future__ import annotations

import argparse
import socket
import time

from src.shared.infra.protocol import EventProtocol


class ViewerClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port

    def subscribe(self, topic: str) -> None:
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(EventProtocol.build_subscribe(topic, subscriber_id="viewer").encode("utf-8"))
            print(f"Assinado em: {topic}")
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                message = EventProtocol.parse_message(data.decode("utf-8"))
                print(f"Notificação recebida: {message}")
                time.sleep(0.2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente assinante do canal de eventos esportivos.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do broker.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do broker.")
    parser.add_argument("--topic", type=str, default="match.events", help="Tópico para assinar.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    viewer = ViewerClient(host=args.host, port=args.port)
    viewer.subscribe(args.topic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
