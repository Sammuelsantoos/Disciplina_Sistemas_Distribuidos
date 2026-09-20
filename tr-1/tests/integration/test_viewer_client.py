"""Testes de integração para o SportsViewerClient."""

import json
import socket
import unittest
from unittest.mock import MagicMock, patch
from src.client.viewer_client import SportsViewerClient


class ViewerClientTests(unittest.TestCase):
    """Testa a inicialização e o processamento de pacotes UDP do viewer."""

    @patch("socket.socket")
    def test_initialization_sets_socket_options(self, mock_socket_class):
        """Verifica as propriedades de reutilização de endereço do socket."""
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        SportsViewerClient(multicast_group="230.0.0.1", multicast_port=6000)

        mock_socket_instance.setsockopt.assert_any_call(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )

    def test_display_notification_handles_valid_json(self):
        """Valida se o interpretador de payloads processa mensagens sem quebrar."""
        client = SportsViewerClient()
        payload = {"tipo": "GOL", "mensagem": "Gol do mandante!"}
        raw_line = json.dumps(payload)

        try:
            # type: ignore
            client._display_notification(raw_line)  # pylint: disable=protected-access
            success = True
        except (json.JSONDecodeError, ValueError):
            success = False

        self.assertTrue(success)

    def test_display_notification_ignores_invalid_json(self):
        """Garante que payloads JSON corrompidos ou inválidos sejam ignorados."""
        client = SportsViewerClient()
        invalid_raw_line = '{"tipo": "GOL", "mensagem":'

        try:
            # type: ignore
            client._display_notification(invalid_raw_line)  # pylint: disable=protected-access
            success = True
        except (json.JSONDecodeError, ValueError):
            success = False

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
