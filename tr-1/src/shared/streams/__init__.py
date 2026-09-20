"""Pacote de fluxos (streams) para leitura e escrita de eventos esportivos."""

from .event_output import MatchEventOutputStream
from .event_input import MatchEventInputStream

__all__ = [
    "MatchEventOutputStream",
    "MatchEventInputStream",
]
