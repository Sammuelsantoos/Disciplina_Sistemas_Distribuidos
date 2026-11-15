"""Cliente TCP para envio de eventos de futebol via RPC em Python."""

import argparse
import socket

from src.shared.infra.protocol import RequestReplyProtocol


class FootballClient:
    """Cliente simples para enviar eventos de futebol ao servidor."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port

    def call(self, team: str = "Flamengo", event_type: str = "gol", minute: str = "13'") -> str:
        method = "register_goal" if event_type == "gol" else "register_card"
        request = RequestReplyProtocol.build_request(
            "MatchService",
            method,
            {"team": team, "player": "Jogador", "minute": minute},
        )
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(request.encode("utf-8"))
            print(f"Requisição enviada: {request}")
            response = sock.recv(4096).decode("utf-8")
        print(f"Resposta do servidor: {response}")
        return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cliente RPC de eventos de futebol em Python.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor.")
    parser.add_argument("--team", type=str, default="Flamengo", help="Time envolvido no evento.")
    parser.add_argument("--event-type", type=str, default="gol", help="Tipo de evento: gol, cartao ou substituicao.")
    parser.add_argument("--minute", type=str, default="13'", help="Minuto do evento.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    client = FootballClient(host=args.host, port=args.port)
    client.call(team=args.team, event_type=args.event_type, minute=args.minute)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
