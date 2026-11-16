"""Cliente assinante (Subscriber) para a arquitetura Publicar/Assinar (Pub/Sub).

Este módulo conecta-se ao servidor Broker via TCP, inscreve-se em um tópico
de eventos esportivos e escuta continuamente as notificações em tempo real.
"""

from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import EventProtocol


class ViewerClient:
    """Cliente espectador que assina tópicos e exibe notificações em texto limpo."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """Inicializa o cliente assinante com o endereço e porta do Broker."""
        self.host = host
        self.port = port

    def subscribe(self, topic: str, subscriber_id: str = "viewer") -> None:
        """Conecta ao Broker, assina o tópico e escuta mensagens continuamente."""
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.settimeout(None)

            sub_msg = EventProtocol.build_subscribe(topic, subscriber_id=subscriber_id)
            sock.sendall(sub_msg.encode("utf-8"))
            print(f"Conectado ao Broker ({self.host}:{self.port}). Tópico: '{topic}'")

            while True:
                data = sock.recv(4096)
                if not data:
                    print("Conexão encerrada pelo servidor Broker.")
                    break

                raw_text = data.decode("utf-8").strip()
                if not raw_text:
                    continue

                for line in raw_text.splitlines():
                    message = EventProtocol.parse_message(line)
                    self._display_message(message)

    @staticmethod
    def _display_message(message: dict) -> None:
        """Formata e exibe no console as confirmações e notificações em texto."""
        action = message.get("action")

        if action == "ACK":
            status = message.get("status", "OK")
            print(f"[BROKER] Inscrição confirmada ({status})\n")
            return

        if action == "NOTIFY":
            payload = message.get("payload", {})
            if not isinstance(payload, dict):
                print(f"[EVENTO] {payload}")
                return

            event_type = str(payload.get("event_type", "EVENTO")).upper()
            match_id = payload.get("match_id", 1)

            if event_type == "CREATE_MATCH":
                home = payload.get("home_team", "Mandante")
                away = payload.get("away_team", "Visitante")
                print(f"Partida cadastrada: [{match_id}] {home} x {away}")
                return

            desc = payload.get("description", "")
            home_team = payload.get("home_team")
            away_team = payload.get("away_team")
            home_score = payload.get("home_score")
            away_score = payload.get("away_score")

            if home_team and away_team and home_score is not None:
                print(
                    f"[{event_type}] [{match_id}] {home_team} {home_score} x "
                    f"{away_score} {away_team} - {desc}"
                )
            elif home_score is not None and away_score is not None:
                print(
                    f"[{event_type}] [{match_id}] Placar: {home_score} x "
                    f"{away_score} - {desc}"
                )
            else:
                print(f"[{event_type}] [{match_id}] {desc}")
            return


def build_parser() -> argparse.ArgumentParser:
    """Configura e retorna o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Cliente assinante do canal de eventos esportivos."
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host do broker.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do broker.")
    parser.add_argument(
        "--topic", type=str, default="match.events", help="Tópico para assinar."
    )
    parser.add_argument(
        "--id", type=str, default="viewer", help="Identificador deste assinante."
    )
    return parser


def main(argv=None) -> int:
    """Ponto de entrada principal para execução do cliente assinante via CLI."""
    args = build_parser().parse_args(argv)
    viewer = ViewerClient(host=args.host, port=args.port)
    try:
        viewer.subscribe(args.topic, subscriber_id=args.id)
    except KeyboardInterrupt:
        print("\nEncerrando cliente assinante...")
    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar ao Broker em {args.host}:{args.port}.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
