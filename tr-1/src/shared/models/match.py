class Match:
    def __init__(self, match_id: int, home_team: str, away_team: str, home_score: int = 0, away_score: int = 0):
        """
        Representa a classe para armazenar os dados de uma partida.
        """
        self.match_id = int(match_id)
        self.home_team = str(home_team)
        self.away_team = str(away_team)
        self.home_score = int(home_score)
        self.away_score = int(away_score)

    def to_csv_line(self) -> str:
        """
        Serializa o objeto Match em uma linha de texto no formato CSV.
        Inclui uma quebra de linha ao final para demarcar o fim do registro.
        """
        return f"{self.match_id},{self.home_team},{self.away_team},{self.home_score},{self.away_score}\n"

    @staticmethod
    def from_csv_line(line: str):
        """
        Desserializa uma linha de texto CSV e reconstrói um objeto Match em memória.
        Retorna None se a linha for inválida ou vazia.
        """
        clean_line = line.strip()
        if not clean_line:
            return None
            
        try:
            parts = clean_line.split(',', 4)
            if len(parts) < 5:
                return None
                
            return Match(
                match_id=int(parts[0]),
                home_team=parts[1],
                away_team=parts[2],
                home_score=int(parts[3]),
                away_score=int(parts[4])
            )
        except (ValueError, IndexError):
            return None

    def __repr__(self) -> str:
        """Representação textual amigável do objeto para depuração e logs."""
        return f"Match(ID={self.match_id}, {self.home_team} {self.home_score} x {self.away_score} {self.away_team})"
