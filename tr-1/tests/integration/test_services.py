"""Testes de integração para as regras de negócio e concorrência do MatchService."""

import threading
import unittest
from src.server.services import MatchService


class MatchServiceTests(unittest.TestCase):
    """Testa o gerenciamento de estados, placares e concorrência em memória."""

    def test_score_and_history(self):
        """Verifica o cálculo dinâmico do placar com base nos gols registrados."""
        service = MatchService()
        service.create_match(10, "Ceara", "Fortaleza")
        service.register_event(1, 10, "GOL", "Gol do Ceara", "ceara")
        service.register_event(2, 10, "CARD", "Cartao amarelo", "Fortaleza")

        match = service.get_match(10)
        self.assertEqual((match.home_score, match.away_score), (1, 0))
        self.assertEqual(len(service.get_events(10)), 2)

    def test_concurrent_goal_registration_keeps_every_goal(self):
        """Garante que registros simultâneos de gols sejam thread-safe."""
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


if __name__ == "__main__":
    unittest.main()
