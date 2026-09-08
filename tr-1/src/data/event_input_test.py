"""Teste manual da leitura de eventos CSV.

Execute a partir da raiz ``tr-1`` com:
``python -m src.data.event_input_test``.
"""

from pathlib import Path

from src.shared.streams import MatchEventInputStream


def main() -> None:
    input_file = Path(__file__).with_name("input_test.csv")
    with input_file.open("r", encoding="utf-8") as source:
        events = MatchEventInputStream(source, buffer_size=11).read_all()

    for event in events:
        print(event)
    print(f"{len(events)} evento(s) lido(s) com sucesso.")


if __name__ == "__main__":
    main()
