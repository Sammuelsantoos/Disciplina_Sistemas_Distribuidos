"""Pacote de modelos de dados compartilhados do sistema esportivo."""

from .match import Match
from .match_event import MatchEvent

__all__ = [
    "Match",
    "MatchEvent",
]
