"""Pacote que contém os clientes da central esportiva (Admin e Viewer)."""

from .viewer_client import SportsViewerClient
from .admin_client import SportsAdminClient

__all__ = [
    "SportsViewerClient",
    "SportsAdminClient",
]
