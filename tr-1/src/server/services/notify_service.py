import socket
import json
import time

class NotificationService:
    def __init__(self, multicast_group: str = "230.0.0.1", multicast_port: int = 6000):
        """
        Inicializa o canal de transmissao UDP Multicast utilizando IP Classe D.
        """
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def send_notification(self, notification_type: str, message: str) -> None:
        """
        Serializa os dados em JSON e envia o pacote UDP para todos os torcedores (Questao 4-b).
        """
        payload = {
            "tipo": notification_type.upper(),
            "mensagem": message,
            "timestamp": int(time.time())
        }
        
        try:
            message_bytes = (json.dumps(payload) + "\n").encode("utf-8")
            self.udp_socket.sendto(message_bytes, (self.multicast_group, self.multicast_port))
        except Exception as error:
            print(f"Erro ao transmitir dados via Multicast: {error}")

    def close(self) -> None:
        """Fecha o recurso de transmissao UDP."""
        self.udp_socket.close()
