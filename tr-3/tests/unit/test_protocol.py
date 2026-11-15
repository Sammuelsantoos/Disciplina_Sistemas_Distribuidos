import unittest

from src.shared.infra.protocol import RequestReplyProtocol


class RequestReplyProtocolTests(unittest.TestCase):
    def test_build_and_parse_request_round_trip(self):
        protocol = RequestReplyProtocol()
        request = protocol.build_request(
            "MatchService",
            "register_goal",
            {"team": "Flamengo", "player": "Pedro", "minute": "13'"},
        )

        self.assertIn("register_goal", request)
        parsed = protocol.parse_request(request)
        self.assertEqual(parsed["object_reference"], "MatchService")
        self.assertEqual(parsed["method_id"], "register_goal")


if __name__ == "__main__":
    unittest.main()
