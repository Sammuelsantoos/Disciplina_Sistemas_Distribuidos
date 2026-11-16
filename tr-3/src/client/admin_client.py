"""Painel de administração interativo para a central esportiva via Pub/Sub.

Este módulo fornece uma interface de linha de comando (CLI) interativa para
cadastrar partidas, publicar eventos em tempo real (GOL, CARD, END) e consultar
placares junto ao servidor Broker.
"""

from __future__ import annotations

import argparse
import socket
from typing import Any

from src.shared.infra.protocol import EventProtocol


class SportsAdminClient:
    """Cliente administrativo que publica eventos e consulta o Broker via Pub/Sub."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        topic: str = "match.events",
    ) -> None:
        """Inicializa os parâmetros de conexão com o servidor Broker."""
        self.host = host
        self.port = port
        self.topic = topic

    def connect(self) -> None:
        """Exibe os dados de inicialização e testa a conexão com o Broker."""
        with socket.create_connection((self.host, self.port), timeout=5):
            pass
        print(
            f"Conectado ao Broker em {self.host}:{self.port} "
            f"(Tópico: '{self.topic}') via Pub/Sub."
        )

    def _send_and_receive(self, raw_request: str) -> dict[str, Any]:
        """Envia uma mensagem via socket TCP e retorna a resposta parseada."""
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(raw_request.encode("utf-8"))
            raw_response = sock.recv(4096).decode("utf-8").strip()
            return EventProtocol.parse_message(raw_response)

    def create_match(
        self, match_id: int, home_team: str, away_team: str
    ) -> dict[str, Any]:
        """Publica a criação de uma nova partida no Broker."""
        request = EventProtocol.build_publish(
            self.topic,
            {
                "event_type": "CREATE_MATCH",
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
            },
        )
        return self._send_and_receive(request)

    def register_event(
        self,
        match_id: int,
        event_type: str,
        description: str,
        team: str = "",
        player: str = "",
        event_id: int | None = None,
    ) -> dict[str, Any]:
        """Publica um evento de gol, cartão ou encerramento de partida."""
        payload: dict[str, Any] = {
            "event_type": event_type.upper(),
            "match_id": match_id,
            "description": description,
            "team": team,
            "player": player,
        }
        if event_id is not None:
            payload["event_id"] = event_id

        request = EventProtocol.build_publish(self.topic, payload)
        return self._send_and_receive(request)

    def query(self, query_type: str, match_id: int = 1) -> dict[str, Any]:
        """Consulta placar, histórico de eventos ou lista de partidas no Broker."""
        request = EventProtocol.build_query(
            query_type, topic=self.topic, match_id=match_id
        )
        return self._send_and_receive(request)

    def start(self) -> None:
        """Inicia o menu interativo do painel administrativo."""
        try:
            self.connect()
            while True:
                print("\n=== PAINEL ADMINISTRATIVO (PUB/SUB) ===")
                print("1. Cadastrar partida")
                print("2. Registrar evento (GOL, CARD ou END)")
                print("3. Consultar placar de uma partida")
                print("4. Listar eventos de uma partida")
                print("5. Listar todas as partidas")
                print("6. Sair")

                option = input("Escolha uma opção: ").strip()

                if option == "1":
                    response = self.create_match(
                        self._read_int("ID da partida: "),
                        input("Time mandante: ").strip(),
                        input("Time visitante: ").strip(),
                    )
                    self._print_ack(response, "Partida cadastrada com sucesso!")

                elif option == "2":
                    match_id = self._read_int("ID da partida: ")
                    event_type = input("Tipo (GOL, CARD ou END): ").strip().upper()
                    team = ""
                    player = ""

                    if event_type == "GOL":
                        team = input("Time que marcou: ").strip()
                        player = input("Jogador que marcou (opcional): ").strip()
                    elif event_type == "CARD":
                        team = input("Time do jogador: ").strip()
                        player = input("Jogador advertido: ").strip()

                    description = input("Descrição (ex: Pedro marcou aos 18'): ").strip()
                    response = self.register_event(
                        match_id=match_id,
                        event_type=event_type,
                        description=description,
                        team=team,
                        player=player,
                    )
                    self._print_ack(response, "Evento publicado e salvo no CSV!")

                elif option == "3":
                    match_id = self._read_int("ID da partida: ")
                    response = self.query("score", match_id=match_id)
                    self._print_query_result(response)

                elif option == "4":
                    match_id = self._read_int("ID da partida: ")
                    response = self.query("events", match_id=match_id)
                    self._print_query_result(response)

                elif option == "5":
                    response = self.query("matches")
                    self._print_query_result(response)

                elif option == "6":
                    print("Encerrando painel...")
                    break
                else:
                    print("Opção inválida. Tente novamente.")

        except (RuntimeError, OSError) as error:
            print(f"\nErro de conexão com o Broker: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nPainel encerrado.")

    @staticmethod
    def _print_ack(response: dict[str, Any], success_msg: str) -> None:
        """Exibe o resultado de uma publicação (PUBLISHED ou ERROR)."""
        status = response.get("status", "ERROR")
        payload = response.get("payload", {})
        if status == "ERROR":
            print(f"[ERRO] {payload.get('message', 'Falha ao processar ação.')}")
        else:
            print(f"[SUCESSO] {success_msg}")

    @staticmethod
    def _print_query_result(response: dict[str, Any]) -> None:
        """Formata e exibe o retorno das consultas síncronas."""
        status = response.get("status", "ERROR")
        payload = response.get("payload")
        if status == "ERROR":
            print(f"[ERRO] {payload.get('message', 'Erro na consulta.')}")
            return

        if isinstance(payload, dict):
            if "home_team" in payload:
                print(
                    f"\nPlacar (Jogo {payload['match_id']}): "
                    f"{payload['home_team']} {payload['home_score']} x "
                    f"{payload['away_score']} {payload['away_team']}"
                )
            elif not payload:
                print("\nNenhuma partida cadastrada.")
            else:
                print("\nPartidas cadastradas:")
                for m_id, summary in payload.items():
                    print(f"  - ID {m_id}: {summary}")
        elif isinstance(payload, list):
            if not payload:
                print("\nNenhum evento registrado para esta partida.")
            else:
                print("\nHistórico de eventos:")
                for evt in payload:
                    print(f"  - [{evt.get('event_type')}] {evt.get('description')}")

    @staticmethod
    def _read_int(prompt: str) -> int:
        """Garante a leitura de um número inteiro válido no terminal."""
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Informe um número inteiro válido.")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser para receber host, porta e tópico via linha de comando."""
    parser = argparse.ArgumentParser(
        description="Painel administrativo interativo do sistema esportivo (Pub/Sub)."
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="IP ou hostname do Broker."
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Porta do servidor Broker."
    )
    parser.add_argument(
        "--topic", type=str, default="match.events", help="Tópico padrão de publicação."
    )
    return parser


def main(argv=None) -> int:
    """Ponto de entrada do painel administrativo."""
    args = build_parser().parse_args(argv)
    client = SportsAdminClient(host=args.host, port=args.port, topic=args.topic)
    client.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
