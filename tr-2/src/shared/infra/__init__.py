"""Pacote de infraestrutura para os protocolos de rede de alto nível."""

from .protocol import RequestReplyProtocol, RemoteObjectRef

__all__ = [
    "RequestReplyProtocol",
    "RemoteObjectRef",
]
