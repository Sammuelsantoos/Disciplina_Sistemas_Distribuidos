"""Leitura incremental de eventos em formato CSV.

O protocolo usado pelo projeto delimita cada evento por uma quebra de linha.
Esta classe mantém os bytes recebidos que ainda não formam uma linha completa,
o que é essencial para sockets TCP, onde uma chamada a ``recv`` pode terminar
no meio de um registro.
"""

from __future__ import annotations

from typing import List, Optional

from src.shared.models import MatchEvent


class MatchEventInputStream:
    """Reconstrói :class:`MatchEvent` a partir de arquivo, terminal ou socket."""

    def __init__(self, source_stream, buffer_size: int = 1024):
        if not hasattr(source_stream, "read") and not hasattr(source_stream, "recv"):
            raise TypeError("A origem deve disponibilizar read() ou recv().")
        if buffer_size <= 0:
            raise ValueError("buffer_size deve ser maior que zero.")

        self.source = source_stream
        self.buffer_size = int(buffer_size)
        self._buffer = ""
        self._finished = False

    def read_event(self) -> Optional[MatchEvent]:
        """Lê o próximo evento completo disponível.

        Retorna ``None`` no fim da origem. Linhas vazias ou inválidas são
        ignoradas, permitindo que um arquivo de histórico contenha separadores
        ou um registro corrompido sem interromper os demais.
        """
        while True:
            newline_at = self._buffer.find("\n")
            if newline_at >= 0:
                line = self._buffer[:newline_at]
                self._buffer = self._buffer[newline_at + 1 :]
                event = MatchEvent.from_csv_line(line)
                if event is not None:
                    return event
                continue

            if self._finished:
                if not self._buffer:
                    return None
                line, self._buffer = self._buffer, ""
                return MatchEvent.from_csv_line(line)

            chunk = self._read_chunk()
            if not chunk:
                self._finished = True
            else:
                self._buffer += chunk

    def read_all(self, count: Optional[int] = None) -> List[MatchEvent]:
        """Lê até ``count`` eventos; sem limite, lê até o fim da origem."""
        if count is not None and count < 0:
            raise ValueError("count não pode ser negativo.")

        events: List[MatchEvent] = []
        while count is None or len(events) < count:
            event = self.read_event()
            if event is None:
                break
            events.append(event)
        return events

    # Alias intuitivo para consumidores que tratam o wrapper como um stream.
    read_next = read_event

    def _read_chunk(self) -> str:
        if hasattr(self.source, "recv"):
            chunk = self.source.recv(self.buffer_size)
        else:
            chunk = self.source.read(self.buffer_size)

        if isinstance(chunk, bytes):
            return chunk.decode("utf-8")
        if isinstance(chunk, str):
            return chunk
        if chunk is None:
            return ""
        raise TypeError("A origem retornou dados que não são texto nem bytes.")
