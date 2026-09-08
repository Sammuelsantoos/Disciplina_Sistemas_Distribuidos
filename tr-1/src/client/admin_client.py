"""Painel de administração para a central esportiva via TCP."""

from __future__ import annotations

import json
import socket
from typing import Any, Dict


class SportsAdminClient:
    """Cliente TCP que envia comandos JSON ao ``LiveSportsServer``."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        self.host = host
        self.port = int(port)
        self.socket: socket.socket | None = None
        self._response_buffer = ""

    def connect(self) -> None:
        """Abre uma conexão TCP com o servidor central."""
        if self.socket is not None:
            return
        self.socket = socket.create_connection((self.host, self.port))
        print(f"Conectado à central esportiva em {self.host}:{self.port}.")

    def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envia uma requisição e aguarda sua resposta JSON delimitada por linha."""
        if self.socket is None:
            raise ConnectionError("Cliente não conectado. Chame connect() primeiro.")

        serialized = json.dumps(payload, ensure_ascii=False) + "\n"
        self.socket.sendall(serialized.encode("utf-8"))
        return self._receive_response()

    def create_match(self, match_id: int, home_team: str, away_team: str) -> Dict[str, Any]:
        """Solicita o cadastro de uma nova partida."""
        return self.send_request(
            {
                "action": "CREATE_MATCH",
                "match_id": match_id,
                "home_team": home_team,
                "away_team": away_team,
            }
        )

    def register_event(
        self,
        event_id: int,
        match_id: int,
        event_type: str,
        description: str,
        team: str = "",
    ) -> Dict[str, Any]:
        """Solicita o registro de gol, cartão ou encerramento de partida."""
        return self.send_request(
            {
                "action": "REGISTER_EVENT",
                "event_id": event_id,
                "match_id": match_id,
                "event_type": event_type.upper(),
                "description": description,
                "team": team,
            }
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
        except (ConnectionError, OSError) as error:
            print(f"Não foi possível conectar à central: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nPainel encerrado.")
        finally:
            self.close()

    def close(self) -> None:
        """Encerra a conexão TCP ativa, caso exista."""
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.socket = None

    def _receive_response(self) -> Dict[str, Any]:
        while "\n" not in self._response_buffer:
            if self.socket is None:  # proteção para analisadores estáticos
                raise ConnectionError("Conexão encerrada.")
            data = self.socket.recv(1024)
            if not data:
                raise ConnectionError("Conexão encerrada pelo servidor.")
            self._response_buffer += data.decode("utf-8")

        line, self._response_buffer = self._response_buffer.split("\n", 1)
        try:
            response = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("Resposta inválida recebida do servidor.") from error
        if not isinstance(response, dict):
            raise ValueError("A resposta do servidor deve ser um objeto JSON.")
        return response

    @staticmethod
    def _read_int(prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Informe um número inteiro válido.")


if __name__ == "__main__":
    SportsAdminClient().start()
