import io
import json
import socket
import threading
import unittest

from src.client.admin_client import SportsAdminClient
from src.server.services import MatchService
from src.shared.streams import MatchEventInputStream


class FragmentedSource:
    """Origem de teste que simula fragmentação comum em TCP."""

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def read(self, _size):
        return next(self.chunks, "")


class MatchEventInputStreamTests(unittest.TestCase):
    def test_reads_events_from_csv_file(self):
        source = io.StringIO(
            "1,5,GOL,Gol do mandante,1700000000\n"
            "2,5,END,Fim de jogo,1700000600\n"
        )
        events = MatchEventInputStream(source).read_all()

        self.assertEqual([event.event_id for event in events], [1, 2])
        self.assertEqual(events[0].event_type, "GOL")

    def test_reassembles_fragmented_records_and_skips_invalid_lines(self):
        source = FragmentedSource(
            ["1,5,GOL,Go", "l,1700000000\ninvalida\n2,5,END", ",Fim,1700000600\n"]
        )
        events = MatchEventInputStream(source, buffer_size=4).read_all()

        self.assertEqual([event.event_id for event in events], [1, 2])


class MatchServiceTests(unittest.TestCase):
    def test_score_and_history(self):
        service = MatchService()
        service.create_match(10, "Ceara", "Fortaleza")
        service.register_event(1, 10, "GOL", "Gol do Ceara", "ceara")
        service.register_event(2, 10, "CARD", "Cartao amarelo", "Fortaleza")

        match = service.get_match(10)
        self.assertEqual((match.home_score, match.away_score), (1, 0))
        self.assertEqual(len(service.get_events(10)), 2)

    def test_concurrent_goal_registration_keeps_every_goal(self):
        service = MatchService()
        service.create_match(20, "A", "B")
        workers = [
            threading.Thread(
                target=service.register_event,
                args=(event_id, 20, "GOL", f"Gol {event_id}", "A"),
            )
            for event_id in range(1, 51)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

        self.assertEqual(service.get_match(20).home_score, 50)
        self.assertEqual(len(service.get_events(20)), 50)


class AdminClientTests(unittest.TestCase):
    def test_request_and_fragmented_response(self):
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
