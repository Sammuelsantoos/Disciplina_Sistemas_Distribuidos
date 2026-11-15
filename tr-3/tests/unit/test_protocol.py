import unittest

from src.shared.infra.protocol import EventProtocol


class EventProtocolTests(unittest.TestCase):
    def test_build_and_parse_publish_round_trip(self):
        payload = EventProtocol.build_publish(
            "match.events",
            {"event_type": "gol", "team": "Flamengo", "player": "Pedro", "minute": "13'"},
        )

        self.assertIn("match.events", payload)
        parsed = EventProtocol.parse_message(payload)
        self.assertEqual(parsed["topic"], "match.events")
        self.assertEqual(parsed["action"], "PUBLISH")


if __name__ == "__main__":
    unittest.main()
