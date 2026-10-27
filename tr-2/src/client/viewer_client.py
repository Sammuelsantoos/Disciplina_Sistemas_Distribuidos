"""Módulo do cliente de visualização de eventos esportivos (Viewer Client).

Este módulo gerencia o consumo de placares e dados esportivos em tempo real
utilizando chamadas remotas estruturadas sobre o protocolo Requisição-Resposta.
"""

import argparse
import json
from typing import Any

from src.shared.infra.protocol import RequestReplyProtocol, RemoteObjectRef


class SportsViewerClient:
    """Cliente que consome dados da central utilizando exclusivamente chamadas RPC."""

    def __init__(self, host: str = "10.10.231.223", port: int = 5000) -> None:
        """Inicializa os parâmetros do servidor e instancia o protocolo de requisição."""
        self.host = host
        self.port = port
        self.protocol = RequestReplyProtocol()
        self.remote_obj = RemoteObjectRef("CentralSportsService")
        self.is_running = True

    def start(self) -> None:
        """Inicia a interface de comandos e o fluxo de execução síncrono do torcedor."""
        self._run_user_interface()

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

    def fetch_score(self, match_id: int) -> None:
        """Busca o placar atual de uma partida enviando uma requisição remota."""
        try:
            response = self.send_request(
                method_id="get_score",
                payload={"match_id": match_id},
            )
            print(f"\n[PLACAR REMOTO]: {response.get('message', 'Sem dados')}")
        except (RuntimeError, OSError) as error:
            print(f"Não foi possível obter os dados da partida: {error}")

    def list_matches(self) -> None:
        """Lista o placar consolidado de todos os confrontos salvos na central."""
        try:
            response = self.send_request(
                method_id="list_matches",
                payload={},
            )
            matches = response.get("matches", {})
            if not matches:
                print("\nNenhuma partida ativa registrada no momento.")
                return
            print("\n--- Partidas em Andamento ---")
            for m_id, scoreboard in matches.items():
                print(f"Partida [{m_id}]: {scoreboard}")
        except (RuntimeError, OSError) as error:
            print(f"Não foi possível listar as partidas: {error}")

    def fetch_events(self, match_id: int) -> None:
        """Busca o histórico de eventos de uma partida enviando uma requisição remota."""
        try:
            response = self.send_request(
                method_id="get_events",
                payload={"match_id": match_id},
            )
            events = response.get("events", [])
            if not events:
                print("\nNenhum lance registrado para esta partida ainda.")
                return
            print("\n--- Histórico de Lances do Jogo ---")
            for evt_msg in events:
                print(evt_msg)
        except (RuntimeError, OSError) as error:
            print(f"Não foi possível obter os lances da partida: {error}")

    def _run_user_interface(self) -> None:
        """Mantém o menu interativo de comandos ativo para consultas do torcedor."""
        print("=== BEM-VINDO À CENTRAL DE ESPORTES EM TEMPO REAL ===")
        print("Conectado com sucesso ao canal de consulta RPC.")

        try:
            while self.is_running:
                print(
                    "\n1. Listar todas as partidas\n2. Consultar placar específico" \
                    "\n3. Ver lances de uma partida\n4. Sair"
                )
                choice = input("Escolha uma opção: ").strip()

                if choice == "1":
                    self.list_matches()
                elif choice == "2":
                    try:
                        m_id = int(input("Informe o ID da partida: ").strip())
                        self.fetch_score(m_id)
                    except ValueError:
                        print("ID inválido.")
                elif choice == "3":
                    try:
                        m_id = int(input("Informe o ID da partida: ").strip())
                        self.fetch_events(m_id)
                    except ValueError:
                        print("ID inválido.")
                elif choice == "4":
                    print("Saindo do painel de monitoramento de torcedores...")
                    self.is_running = False
                else:
                    print("Opção inválida.")
        except (KeyboardInterrupt, EOFError):
            self.is_running = False
        print("Conexão com a central esportiva encerrada.")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser para receber o endereço do servidor e a porta via linha de comando."""
    parser = argparse.ArgumentParser(
        description="Cliente torcedor para obter consultas de placares via RPC."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="10.10.231.223",
        help="IP ou hostname da central esportiva.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Porta de escuta do servidor central.",
    )
    return parser


def main(argv=None) -> int:
    """Executa o cliente torcedor usando argumentos de linha de comando."""
    args = build_parser().parse_args(argv)
    client = SportsViewerClient(host=args.host, port=args.port)
    client.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
