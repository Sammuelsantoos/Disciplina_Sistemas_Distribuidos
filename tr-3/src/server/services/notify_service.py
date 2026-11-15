from __future__ import annotations


class NotifyService:
    """Serviço auxiliar para formatar mensagens de notificação do evento."""

    @staticmethod
    def format_message(event: dict) -> str:
        event_type = event.get("event_type", "evento")
        description = event.get("description", "Ação do jogo registrada.")
        return f"{event_type}: {description}"
