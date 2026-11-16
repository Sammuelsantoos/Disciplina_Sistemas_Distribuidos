"""Cliente produtor (Publisher) para a arquitetura Publicar/Assinar (Pub/Sub).

Este módulo permite que um administrador crie partidas, publique eventos em
tempo real (gols, cartões, encerramento) e consulte o placar ou histórico
junto ao Broker via sockets TCP.
"""

from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import EventProtocol


class AdminClient:
    """Cliente administrativo responsável por publicar eventos e consultar o Broker."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """Inicializa o cliente com o endereço e porta do servidor Broker."""
        self.host = host
        self.port = port

    def _send_and_receive(self, raw_request: str) -> str:
        """Abre conexão TCP, envia uma mensagem formatada e retorna a resposta."""
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(raw_request.encode("utf-8"))
            return sock.recv(4096).decode("utf-8").strip()

    def publish(self, topic: str, event: dict) -> str:
        """Publica um evento em um tópico específico e exibe a confirmação."""
        request = EventProtocol.build_publish(topic, event)
        response = self._send_and_receive(request)
        print(f"Evento publicado: {request.strip()}")
        print(f"Resposta do broker: {response}")
        return response

    def query(self, query_type: str, topic: str, match_id: int = 1) -> str:
        """Consulta dados síncronos (placar, eventos ou partidas) no Broker."""
        request = EventProtocol.build_query(query_type, topic=topic, match_id=match_id)
        response = self._send_and_receive(request)
        print(f"Resposta da consulta ({query_type}): {response}")
        return response


def build_parser() -> argparse.ArgumentParser:
    """Configura e retorna o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Cliente produtor em arquitetura publicar e assinar."
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do broker.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do broker.")
    parser.add_argument(
        "--action",
        choices=[
            "create-match",
            "goal",
            "card",
            "end",
            "query-score",
            "query-events",
            "query-matches",
        ],
        required=True,
        help="Ação a ser executada no Broker.",
    )
    parser.add_argument(
        "--match-id", type=int, default=1, help="ID numérico da partida."
    )
    parser.add_argument(
        "--topic", type=str, default="match.events", help="Tópico de publicação."
    )
    parser.add_argument(
        "--home-team", type=str, default="Flamengo", help="Time mandante (create-match)."
    )
    parser.add_argument(
        "--away-team", type=str, default="Vasco", help="Time visitante (create-match)."
    )
    parser.add_argument(
        "--team", type=str, default="Flamengo", help="Time autor do evento."
    )
    parser.add_argument(
        "--player", type=str, default="Pedro", help="Jogador autor do evento."
    )
    parser.add_argument(
        "--minute", type=str, default="13'", help="Minuto da partida."
    )
    return parser


def main(argv=None) -> int:
    """Ponto de entrada principal para execução do cliente produtor via CLI."""
    args = build_parser().parse_args(argv)
    client = AdminClient(host=args.host, port=args.port)

    if args.action == "create-match":
        client.publish(
            args.topic,
            {
                "event_type": "CREATE_MATCH",
                "match_id": args.match_id,
                "home_team": args.home_team,
                "away_team": args.away_team,
            },
        )
    elif args.action == "goal":
        client.publish(
            args.topic,
            {
                "event_type": "GOL",
                "match_id": args.match_id,
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
                "event_type": "CARD",
                "match_id": args.match_id,
                "team": args.team,
                "player": args.player,
                "minute": args.minute,
                "description": f"Cartão para {args.player} do {args.team} aos {args.minute}.",
            },
        )
    elif args.action == "end":
        client.publish(
            args.topic,
            {
                "event_type": "END",
                "match_id": args.match_id,
                "description": "Partida encerrada.",
            },
        )
    elif args.action == "query-score":
        client.query("score", topic="match.status", match_id=args.match_id)
    elif args.action == "query-events":
        client.query("events", topic="match.events", match_id=args.match_id)
    elif args.action == "query-matches":
        client.query("matches", topic="match.status", match_id=args.match_id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
