"""Testes de ponta a ponta (E2E) para o LiveSportsServer."""

import json
import socket
import threading
import time
import unittest
from src.server.main_server import LiveSportsServer


class LiveSportsServerE2ETests(unittest.TestCase):
    """Valida o ciclo de vida completo, roteamento TCP e concorrência do servidor."""

    def setUp(self):
        """Inicializa o servidor real em uma porta dinâmica livre."""
        self.host = "127.0.0.1"

        self.server = LiveSportsServer(tcp_host=self.host, tcp_port=0)

        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        time.sleep(0.1)

        self.port = self.server.tcp_socket.getsockname()[1]

    def tearDown(self):
        """Garante o encerramento limpo do socket do servidor após cada teste."""
        # type: ignore
        self.server._cleanup()  # pylint: disable=protected-access
        self.server_thread.join(timeout=1.0)

    def test_server_creates_match_via_tcp_request(self):
        """Verifica se o servidor aceita conexões e processa requisições JSON."""
        client_socket = socket.create_connection((self.host, self.port))

        payload = {
            "action": "CREATE_MATCH",
            "match_id": 99,
            "home_team": "Ceara",
            "away_team": "Fortaleza"
        }

        request_bytes = (json.dumps(payload) + "\n").encode("utf-8")
        client_socket.sendall(request_bytes)

        response_bytes = client_socket.recv(1024)
        response = json.loads(response_bytes.decode("utf-8").strip())

        client_socket.close()

        self.assertEqual(response.get("status"), "SUCCESS")

    def test_server_rejects_invalid_operation(self):
        """Garante que o roteador trate e responda erros para comandos desconhecidos."""
        client_socket = socket.create_connection((self.host, self.port))

        payload = {"action": "INVALID_ACTION"}
        request_bytes = (json.dumps(payload) + "\n").encode("utf-8")
        client_socket.sendall(request_bytes)

        response_bytes = client_socket.recv(1024)
        response = json.loads(response_bytes.decode("utf-8").strip())

        client_socket.close()

        self.assertEqual(response.get("status"), "ERROR")


if __name__ == "__main__":
    unittest.main()
