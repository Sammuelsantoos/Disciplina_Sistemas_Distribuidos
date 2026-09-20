"""Testes de integração para a comunicação TCP do SportsAdminClient."""

import json
import socket
import threading
import unittest
from src.client.admin_client import SportsAdminClient


class AdminClientTests(unittest.TestCase):
    """Testa a serialização e troca de mensagens TCP entre cliente e rede."""

    def test_request_and_fragmented_response(self):
        """Verifica o envio de requisições e a leitura de respostas fragmentadas."""
        client_socket, server_socket = socket.socketpair()
        client = SportsAdminClient()
        client.socket = client_socket

        def respond():
            request = server_socket.recv(1024).decode("utf-8")
            self.assertEqual(json.loads(request), {
                "action": "CREATE_MATCH",
                "match_id": 7,
                "home_team": "A",
                "away_team": "B",
            })
            server_socket.sendall(b'{"status":"SUCCESS",')
            server_socket.sendall(b'"message":"ok"}\n')

        server_thread = threading.Thread(target=respond)
        server_thread.start()
        self.assertEqual(client.create_match(7, "A", "B")["status"], "SUCCESS")
        server_thread.join()
        client.close()
        server_socket.close()


if __name__ == "__main__":
    unittest.main()
