"""Teste manual da leitura de eventos CSV."""

from pathlib import Path
from src.shared.streams import MatchEventInputStream


def run_input() -> None:
    """Busca o arquivo CSV de teste e processa seu fluxo de dados."""
    root_project = Path(__file__).resolve().parents[2]
    input_file = root_project / "src" / "data" / "input_test.csv"

    with input_file.open("r", encoding="utf-8") as source:
        events = MatchEventInputStream(source, buffer_size=4096).read_all()

    for event in events:
        print(event)
    print(f"{len(events)} evento(s) lido(s) com sucesso.")


if __name__ == "__main__":
    run_input()
