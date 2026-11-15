import unittest

from src.server.services.football_service import FootballEventServiceImpl


class FootballEventServiceTests(unittest.TestCase):
    def test_publish_event_returns_expected_message(self):
        service = FootballEventServiceImpl()
        self.assertEqual(
            service.publish_event("Flamengo", "gol", "13'"),
            "Evento de futebol: Flamengo marcou gol aos 13'.",
        )


if __name__ == "__main__":
    unittest.main()
