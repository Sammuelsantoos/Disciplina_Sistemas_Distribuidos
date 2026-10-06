"""Módulo de modelo para eventos de partidas esportivas (MatchEvent).

Gerencia a estrutura, serialização e desserialização de eventos como
gols, cartões e encerramentos em formatos de texto como CSV.
"""

import time


class BaseMatchEvent:
    """Define a base comum para eventos esportivos do sistema."""

    def build_message(self) -> str:
        """Retorna a mensagem textual padronizada do evento."""
        return f"[{self.event_type}] {self.description}"


class MatchEvent(BaseMatchEvent):
    """Representa um evento ocorrido dentro de uma partida de futebol."""

    def __init__(
        self,
        event_id: int,
        match_id: int,
        event_type: str,
        description: str,
        timestamp: int = None
    ):
        """
        Representa a classe para armazenar as informações de um evento de jogo.
        O tipo de evento (event_type) deve seguir os padrões: GOL, CARD ou END.
        """
        self.event_id = int(event_id)
        self.match_id = int(match_id)
        self.event_type = str(event_type).upper()
        self.description = str(description)
        self.timestamp = int(timestamp) if timestamp is not None else int(time.time())

    def to_csv_line(self) -> str:
        """
        Serializa o objeto MatchEvent em uma linha de texto no formato CSV.
        """
        return (
            f"{self.event_id},{self.match_id},{self.event_type},"
            f"{self.description},{self.timestamp}\n"
        )

    @staticmethod
    def from_csv_line(line: str):
        """
        Desserializa uma linha de texto CSV e reconstrói um objeto MatchEvent
        em memória. Retorna None se a linha for inválida ou vazia.
        """
        clean_line = line.strip()
        if not clean_line:
            return None

        try:
            parts = clean_line.split(',', 4)
            if len(parts) < 5:
                return None

            return MatchEvent(
                event_id=int(parts[0]),
                match_id=int(parts[1]),
                event_type=parts[2],
                description=parts[3],
                timestamp=int(parts[4])
            )
        except (ValueError, IndexError):
            return None

    def __repr__(self) -> str:
        """Representação textual amigável do objeto para depuração e logs."""
        return (
            f"MatchEvent(ID={self.event_id}, MatchID={self.match_id}, "
            f"Type={self.event_type}, Desc='{self.description}')"
        )


class GoalEvent(MatchEvent):
    """Evento específico para gol marcado em uma partida."""

    def __init__(self, event_id: int, match_id: int, team: str, description: str | None = None, timestamp: int = None):
        super().__init__(event_id, match_id, "GOL", description or f"Gol do {team}", timestamp)
        self.team = str(team)

    def build_message(self) -> str:
        return f"[GOL] {self.team}"


class CardEvent(MatchEvent):
    """Evento específico para cartões recebidos por jogadores ou times."""

    def __init__(self, event_id: int, match_id: int, player: str, description: str | None = None, timestamp: int = None):
        super().__init__(event_id, match_id, "CARD", description or f"Cartão para {player}", timestamp)
        self.player = str(player)

    def build_message(self) -> str:
        return f"[CARD] {self.player}"
