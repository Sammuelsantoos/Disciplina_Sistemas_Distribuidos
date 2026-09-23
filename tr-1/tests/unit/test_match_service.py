"""Testes de unidade para o MatchService isolando a persistência de streams."""

import unittest
from unittest.mock import MagicMock, patch
from src.server.services.match_service import MatchService
from src.shared.models import MatchEvent


class MatchServiceUnitTests(unittest.TestCase):
    """Garante o comportamento correto das regras de negócio do MatchService."""

    @patch("os.path.exists")
    @patch("builtins.open")
    @patch("src.server.services.match_service.MatchEventInputStream")
    def test_init_loads_historical_events_successfully(
        self, mock_input_stream, mock_open, mock_exists
    ):
        """Verifica se o construtor consome o InputStream histórico se o arquivo existir."""
        mock_exists.return_value = True
        mock_open.return_value = MagicMock()
        mock_stream_instance = MagicMock()
        mock_input_stream.return_value = mock_stream_instance

        historical_event = MatchEvent(1, 100, "GOL", "Gol inicial")
        mock_stream_instance.read_all.return_value = [historical_event]

        service = MatchService(storage_path="src/data/event_test.csv")

        # pylint: disable=protected-access
        self.assertIn(100, service._matches)
        self.assertIn(1, service._event_ids)

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("src.server.services.match_service.MatchEventOutputStream")
    def test_register_event_triggers_output_stream_write(
        self, mock_output_stream, mock_open, mock_makedirs, mock_exists
    ):
        """Garante que a criação de novos eventos faça o envio de dados via OutputStream."""
        mock_exists.return_value = False
        mock_makedirs.return_value = None
        mock_open.return_value = MagicMock()
        mock_stream_instance = MagicMock()
        mock_output_stream.return_value = mock_stream_instance

        service = MatchService(storage_path="src/data/event_test.csv")
        service.create_match(10, "Ceara", "Fortaleza")

        service.register_event(1, 10, "GOL", "Gol de placa", "Ceara")

        mock_output_stream.assert_called_once()
        mock_stream_instance.write_all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
