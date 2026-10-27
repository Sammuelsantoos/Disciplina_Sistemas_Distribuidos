"""Painel de administração para a central esportiva via protocolo Requisição-Resposta."""

from __future__ import annotations

import argparse
import json
from typing import Any

from src.shared.infra import RequestReplyProtocol, RemoteObjectRef


class SportsAdminClient:
    """Cliente administrativo que consome os métodos remotos via RequestReplyProtocol."""

    def __init__(self, host: str = "10.10.231.223", port: int = 5000) -> None:
        """Inicializa os parâmetros do servidor e instancia o protocolo de requisição."""
        self.host = host
        self.port = port
        self.protocol = RequestReplyProtocol()
        self.remote_obj = RemoteObjectRef("CentralSportsService")

    def connect(self) -> None:
        """Garante a compatibilidade de inicialização exibindo os dados de conexão."""
        print(f"Pronto para comunicação com a central em {self.host}:{self.port} via RPC.")

    def send_request(self, method_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Realiza o marshalling do dicionário em JSON e invoca do_operation."""
        serialized_args = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        response_bytes = self.protocol.do_operation(
            o=self.remote_obj,
            method_id=method_id,
            arguments=serialized_args,
            server_host=self.host,
            server_port=self.port,
        )
        return json.loads(response_bytes.decode("utf-8"))

    def create_match(self, match_id: int, home_team: str, away_team: str) -> dict[str, Any]:
        """Solicita o cadastro de uma nova partida via procedimento remoto."""
        return self.send_request(
            method_id="create_match",
            payload={
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
            },
        )

    def register_event(
        self,
        event_id: int,
        match_id: int,
        event_type: str,
        description: str,
        team: str = "",
    ) -> dict[str, Any]:
        """Solicita o registro de gol, cartão ou encerramento de partida via procedimento remoto."""
        return self.send_request(
            method_id="register_event",
            payload={
                "event_id": event_id,
                "match_id": match_id,
                "event_type": event_type.upper(),
                "description": description,
                "team": team,
            },
        )

    def start(self) -> None:
        """Inicia o menu interativo do painel."""
        try:
            self.connect()
            while True:
                print("\n1. Cadastrar partida\n2. Registrar evento\n3. Sair")
                option = input("Escolha uma opção: ").strip()
                if option == "1":
                    response = self.create_match(
                        self._read_int("ID da partida: "),
                        input("Time mandante: ").strip(),
                        input("Time visitante: ").strip(),
                    )
                elif option == "2":
                    event_type = input("Tipo (GOL, CARD ou END): ").strip().upper()
                    team = input("Time envolvido (obrigatório para GOL): ").strip()
                    response = self.register_event(
                        self._read_int("ID do evento: "),
                        self._read_int("ID da partida: "),
                        event_type,
                        input("Descrição: ").strip(),
                        team,
                    )
                elif option == "3":
                    break
                else:
                    print("Opção inválida.")
                    continue
                print(f"{response.get('status', 'ERROR')}: {response.get('message', '')}")
        except (RuntimeError, OSError) as error:
            print(f"Não foi possível conectar à central: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nPainel encerrado.")

    @staticmethod
    def _read_int(prompt: str) -> int:
        """Garante a leitura de um número inteiro válido."""
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Informe um número inteiro válido.")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser para receber host e porta via linha de comando."""
    parser = argparse.ArgumentParser(description="Painel administrativo do sistema esportivo.")
    parser.add_argument("--host", type=str, default="10.10.231.223", help="IP ou hostname do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta do servidor central.")
    return parser


def main(argv=None) -> int:
    """Executa o cliente administrativo usando argumentos de linha de comando."""
    args = build_parser().parse_args(argv)
    client = SportsAdminClient(host=args.host, port=args.port)
    client.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
