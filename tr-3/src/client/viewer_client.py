from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import RequestReplyProtocol


class ViewerClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port

    def query(self, method: str) -> str:
        request = RequestReplyProtocol.build_request("MatchService", method, {})
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(request.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8")
        print(f"Requisição enviada: {request}")
        print(f"Resposta do servidor: {response}")
        return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente torcedor para consulta do placar e eventos.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor.")
    parser.add_argument("--action", choices=["score", "events"], required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    client = ViewerClient(host=args.host, port=args.port)
    if args.action == "score":
        client.query("get_score")
    elif args.action == "events":
        client.query("get_events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
