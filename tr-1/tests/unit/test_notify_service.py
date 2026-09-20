"""Testes unitários para o serviço de notificação."""

import json
import socket
import unittest
from unittest.mock import MagicMock, patch
from src.server.services.notify_service import NotificationService


class NotificationServiceTests(unittest.TestCase):
    """Garante o comportamento isolado do montador de payloads UDP Multicast."""

    @patch("socket.socket")
    def test_initialization_sets_multicast_ttl(self, mock_socket_class):
        """Verifica se o construtor configura o socket com o TTL correto."""
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        NotificationService(multicast_group="230.0.0.1", multicast_port=6000)

        mock_socket_instance.setsockopt.assert_any_call(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2
        )

    @patch("socket.socket")
    def test_send_notification_payload_format(self, mock_socket_class):
        """Valida a estrutura do dicionário JSON enviado para a rede."""
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        service = NotificationService(multicast_group="230.0.0.1", multicast_port=6000)
        service.send_notification(notification_type="GOL", message="Gol do Ceará!")

        mock_socket_instance.sendto.assert_called_once()
        args, _ = mock_socket_instance.sendto.call_args

        sent_bytes = args[0]
        destination = args[1]

        self.assertEqual(destination, ("230.0.0.1", 6000))

        sent_string = sent_bytes.decode("utf-8")
        self.assertTrue(sent_string.endswith("\n"))

        payload = json.loads(sent_string.strip())
        self.assertEqual(payload["tipo"], "GOL")
        self.assertEqual(payload["mensagem"], "Gol do Ceará!")
        self.assertIn("timestamp", payload)


if __name__ == "__main__":
    unittest.main()
