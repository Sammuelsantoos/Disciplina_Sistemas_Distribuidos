"""Testes de integração para os componentes de leitura de streams de eventos."""

import io
import unittest
from src.shared.streams import MatchEventInputStream


class FragmentedSource:
    """Origem de teste que simula fragmentação comum em TCP."""

    def __init__(self, chunks):
        self.chunks = iter(chunks)

    def read(self, _size):
        """Retorna o próximo pedaço de dado simulando a rede."""
        return next(self.chunks, "")


class MatchEventInputStreamTests(unittest.TestCase):
    """Testa a reconstrução de eventos a partir de fontes de dados brutos."""

    def test_reads_events_from_csv_file(self):
        """Verifica a leitura correta de eventos válidos a partir de um CSV."""
        source = io.StringIO(
            "1,5,GOL,Gol do mandante,1700000000\n"
            "2,5,END,Fim de jogo,1700000600\n"
        )
        events = MatchEventInputStream(source).read_all()

        self.assertEqual([event.event_id for event in events], [1, 2])
        self.assertEqual(events[0].event_type, "GOL")

    def test_reassembles_fragmented_records_and_skips_invalid_lines(self):
        """Verifica a reconstrução de linhas fragmentadas e descarte de erros."""
        source = FragmentedSource(
            ["1,5,GOL,Go", "l,1700000000\ninvalida\n2,5,END", ",Fim,1700000600\n"]
        )
        events = MatchEventInputStream(source, buffer_size=4).read_all()

        self.assertEqual([event.event_id for event in events], [1, 2])


if __name__ == "__main__":
    unittest.main()
