import sys
from src.shared.models import MatchEvent
from src.shared.streams import MatchEventOutputStream

my_events = [
    MatchEvent(event_id=1, match_id=101, event_type="GOL", description="Gol do Rubens"),
    MatchEvent(event_id=2, match_id=101, event_type="CARD", description="Cartao Amarelo Samuel"),
    MatchEvent(event_id=3, match_id=101, event_type="END", description="Fim do Primeiro Tempo")
]

print("--- TESTE EM TERMINAL ---")
screen_stream = MatchEventOutputStream(sys.stdout, my_events, count=2)
screen_stream.write_all()

print("\n--- TESTE EM ARQUIVO ---")
with open("src/data/output_test.csv", "a", encoding="utf-8") as file_destination:
    file_stream = MatchEventOutputStream(file_destination, my_events, count=3)
    file_stream.write_all()

print("Verifique o arquivo 'src/data/output_test.csv' criado com sucesso.")
