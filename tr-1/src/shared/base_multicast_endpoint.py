"""Classe base compartilhada para endpoints UDP multicast do sistema."""

import socket


class BaseMulticastEndpoint:
    """Define o comportamento comum de sockets multicast usados no projeto."""

    def __init__(self, multicast_group: str = "230.0.0.1", multicast_port: int = 6000, *, ttl: int | None = None):
        self.multicast_group = multicast_group
        self.multicast_port = int(multicast_port)

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if ttl is not None:
            self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def close(self) -> None:
        """Fecha o soquete do endpoint multicast."""
        try:
            self.udp_socket.close()
        except OSError:
            pass
