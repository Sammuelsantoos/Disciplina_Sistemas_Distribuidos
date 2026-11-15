"""Compatibilidade com o antigo nome do módulo do serviço."""

from src.server.services.football_service import FootballEventService, FootballEventServiceImpl

__all__ = ["FootballEventService", "FootballEventServiceImpl"]
