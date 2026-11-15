import unittest

from src.server.services.match_service import MatchService


class MatchServiceTests(unittest.TestCase):
    def test_register_goal_updates_score_and_history(self):
        service = MatchService(home_team="Flamengo", away_team="Vasco")

        result = service.register_goal("Flamengo", "Pedro", "13'")

        self.assertEqual(result["home_score"], 1)
        self.assertEqual(result["away_score"], 0)
        self.assertIn("Pedro", service.get_events()[-1]["description"])

    def test_register_card_adds_event(self):
        service = MatchService(home_team="Flamengo", away_team="Vasco")

        result = service.register_card("Vasco", "João", "42'")

        self.assertIn("cartao", result["event_type"].lower())
        self.assertEqual(len(service.get_events()), 1)


if __name__ == "__main__":
    unittest.main()
