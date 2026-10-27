"""Serviço de envio de notificações via UDP Multicast para os clientes."""

import json
import socket
import time

from src.shared.base_multicast_endpoint import BaseMulticastEndpoint


class NotificationService(BaseMulticastEndpoint):
    """Gerencia a transmissão de alertas e eventos de partidas em tempo real."""

    def __init__(self, multicast_group: str = "230.0.0.1", multicast_port: int = 6000):
        """
        Inicializa o canal de transmissao UDP Multicast utilizando IP Classe D.
        """
        super().__init__(multicast_group=multicast_group, multicast_port=multicast_port, ttl=2)

    def send_notification(self, notification_type: str, message: str) -> None:
        """
        Serializa os dados em JSON e envia o pacote UDP para todos os
        torcedores (Questao 4-b).
        """
        payload = {
            "tipo": notification_type.upper(),
            "mensagem": message,
            "timestamp": int(time.time())
        }

        try:
            message_bytes = (json.dumps(payload) + "\n").encode("utf-8")
            self.udp_socket.sendto(message_bytes, (self.multicast_group, self.multicast_port))
        except socket.error as error:
            print(f"Erro ao transmitir dados via Multicast: {error}")

    def close(self) -> None:
        """Fecha o recurso de transmissao UDP."""
        super().close()
