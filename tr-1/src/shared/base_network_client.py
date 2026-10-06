"""Classe base para clientes de rede do sistema esportivo."""

from __future__ import annotations

import socket


class BaseNetworkClient:
    """Centraliza atributos e operações comuns de clientes TCP/UDP."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = int(port)
        self.socket: socket.socket | None = None

    def connect(self) -> None:
        """Abre a conexão de rede do cliente."""
        raise NotImplementedError("Subclasses devem implementar connect().")

    def close(self) -> None:
        """Fecha a conexão ativa do cliente, se existir."""
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.socket = None
