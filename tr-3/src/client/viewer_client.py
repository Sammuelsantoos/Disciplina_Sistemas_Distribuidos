"""Cliente assinante (Subscriber) para a arquitetura Publicar/Assinar (Pub/Sub).

Este módulo conecta-se ao servidor Broker via TCP, inscreve-se em um tópico
de eventos esportivos e escuta continuamente as notificações em tempo real.
"""

from __future__ import annotations

import argparse
import socket

from src.shared.infra.protocol import EventProtocol


class ViewerClient:
    """Cliente espectador que assina tópicos e exibe notificações em tempo real."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """Inicializa o cliente assinante com o endereço e porta do Broker."""
        self.host = host
        self.port = port

    def subscribe(self, topic: str, subscriber_id: str = "viewer") -> None:
        """Conecta ao Broker, assina o tópico e escuta mensagens continuamente."""
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            # Remove o timeout após conectar para aguardar eventos indefinidamente
            sock.settimeout(None)

            sub_msg = EventProtocol.build_subscribe(topic, subscriber_id=subscriber_id)
            sock.sendall(sub_msg.encode("utf-8"))
            print(f"Conectado ao Broker. Assinado no tópico: '{topic}'...")

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
        """Formata e exibe no console as confirmações (ACK) e notificações (NOTIFY)."""
        action = message.get("action")
        if action == "ACK":
            status = message.get("status")
            print(f"[BROKER] Inscrição confirmada (Status: {status})")
        elif action == "NOTIFY":
            payload = message.get("payload", {})
            desc = payload.get("description", payload)
            home_score = payload.get("home_score")
            away_score = payload.get("away_score")

            if home_score is not None and away_score is not None:
                print(f"\n[AO VIVO] {desc} | Placar: {home_score} x {away_score}")
            else:
                print(f"\n[AO VIVO] {desc}")
        else:
            print(f"Mensagem recebida: {message}")


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
