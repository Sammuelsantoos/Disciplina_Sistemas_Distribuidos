"""Módulo de testes de ponta a ponta (E2E) para o LiveSportsServer."""

import json
import socket
import threading
import time
import unittest
from src.server.main_server import LiveSportsServer


class LiveSportsServerE2ETests(unittest.TestCase):
    """Valida o ciclo de vida completo e o roteamento TCP do servidor."""

    def setUp(self):
        """Inicializa o servidor e aguarda a alocação da porta dinâmica."""
        self.host = "127.0.0.1"
        self.server = LiveSportsServer(tcp_host=self.host, tcp_port=0)

        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()

        for _ in range(20):
            try:
                self.port = self.server.tcp_socket.getsockname()[1]
                if self.port != 0:
                    break
            except OSError:
                pass
            time.sleep(0.01)
        else:
            self.port = self.server.tcp_socket.getsockname()[1]

        time.sleep(0.05)

    def tearDown(self):
        """Encerra o socket do servidor e limpa os recursos do sistema."""
        self.server._cleanup()  # pylint: disable=protected-access
        time.sleep(0.1)

    def test_server_creates_match_via_tcp_request(self):
        """Verifica se o servidor aceita e processa a criação de partidas."""
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
        """Garante que o roteador responda com erro para comandos inválidos."""
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
