"""Testes de integração para as regras de negócio e concorrência do MatchService."""

import os
import threading
import unittest
from src.server.services import MatchService


class MatchServiceTests(unittest.TestCase):
    """Testa o gerenciamento de estados, placares e concorrência em memória."""

    def setUp(self):
        """Define um arquivo de testes isolado e garante que ele comece limpo."""
        self.test_csv = "src/data/event_test_integration.csv"
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        self.service = MatchService(storage_path=self.test_csv)

    def tearDown(self):
        """Limpa o arquivo temporário após a execução de cada teste."""
        if os.path.exists(self.test_csv):
            try:
                os.remove(self.test_csv)
            except OSError:
                pass

    def test_score_and_history(self):
        """Verifica o cálculo dinâmico do placar com base nos gols registrados."""
        self.service.create_match(10, "Ceara", "Fortaleza")
        self.service.register_event(1, 10, "GOL", "Gol do Ceara", "ceara")
        self.service.register_event(2, 10, "CARD", "Cartao amarelo", "Fortaleza")

        match = self.service.get_match(10)
        self.assertEqual((match.home_score, match.away_score), (1, 0))
        self.assertEqual(len(self.service.get_events(10)), 2)

    def test_concurrent_goal_registration_keeps_every_goal(self):
        """Garante que registros simultâneos de gols sejam thread-safe."""
        self.service.create_match(20, "A", "B")
        workers = [
            threading.Thread(
                target=self.service.register_event,
                args=(event_id, 20, "GOL", f"Gol {event_id}", "A"),
            )
            for event_id in range(1, 51)
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

        self.assertEqual(self.service.get_match(20).home_score, 50)
        self.assertEqual(len(self.service.get_events(20)), 50)


if __name__ == "__main__":
    unittest.main()
