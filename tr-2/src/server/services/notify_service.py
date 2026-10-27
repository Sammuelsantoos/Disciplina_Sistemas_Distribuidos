"""Serviço de envio de notificações e log de eventos esportivos."""

import json
import time


class NotificationService:
    """Gerencia a simulação de transmissão de alertas e eventos de partidas em tempo real."""

    def __init__(self, multicast_group: str = "230.0.0.1", multicast_port: int = 6000) -> None:
        """Inicializa as propriedades de configuração do serviço de notificações."""
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port

    def send_notification(self, notification_type: str, message: str) -> None:
        """Serializa os dados em JSON e exibe o alerta localmente no console do servidor."""
        payload = {
            "tipo": notification_type.upper(),
            "mensagem": message,
            "timestamp": int(time.time()),
        }
        print(f"[NOTIFICAÇÃO LOCAL]: {json.dumps(payload, ensure_ascii=False)}")
