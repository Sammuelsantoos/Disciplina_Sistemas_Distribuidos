"""Módulo de infraestrutura para o protocolo de comunicação Requisição-Resposta."""

import json
import xmlrpc.client
from typing import Tuple, Optional


class RemoteObjectRef:
    """Representa uma referência a um objeto remoto no servidor."""

    def __init__(self, object_name: str) -> None:
        """Inicializa a referência do objeto remoto com seu identificador."""
        self.object_name = object_name


class Message:
    """Representa a estrutura de dados empacotada de uma mensagem de rede."""

    def __init__(
        self,
        message_type: int,
        request_id: int,
        object_reference: str,
        method_id: str,
        arguments: bytes,
    ) -> None:
        """Inicializa uma mensagem com os campos obrigatórios do protocolo."""
        self.message_type = message_type
        self.request_id = request_id
        self.object_reference = object_reference
        self.method_id = method_id
        self.arguments = arguments

    def serialize(self) -> str:
        """Converte a estrutura da mensagem em uma string JSON."""
        payload = {
            "messageType": self.message_type,
            "requestId": self.request_id,
            "objectReference": self.object_reference,
            "methodId": self.method_id,
            "arguments": self.arguments.decode("utf-8"),
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def deserialize(data_str: str) -> "Message":
        """Reconstrói uma instância de Message a partir de uma string JSON."""
        payload = json.loads(data_str)
        return Message(
            message_type=payload["messageType"],
            request_id=payload["requestId"],
            object_reference=payload["objectReference"],
            method_id=payload["methodId"],
            arguments=payload["arguments"].encode("utf-8"),
        )


class RequestReplyProtocol:
    """Gerenciador do ciclo de vida das mensagens de Requisição e Resposta."""

    def __init__(self, port: Optional[int] = None) -> None:
        """Inicializa as propriedades do protocolo de comunicação de alto nível."""
        self.port = port
        self.last_client_address: Optional[Tuple[str, int]] = None
        self._server_proxy = None

    def do_operation(
        self,
        o: RemoteObjectRef,
        method_id: str,
        arguments: bytes,
        server_host: str,
        server_port: int,
    ) -> bytes:
        """Envia uma mensagem de requisição e aguarda a resposta correspondente via RPC."""
        if not self._server_proxy:
            self._server_proxy = xmlrpc.client.ServerProxy(f"http://{server_host}:{server_port}/")

        req_msg = Message(0, 1, o.object_name, method_id, arguments)
        response_str = self._server_proxy.execute_action(req_msg.serialize())

        reply_msg = Message.deserialize(response_str)
        return reply_msg.arguments

    def get_request(self) -> Message:
        """Obtém uma requisição interceptada pelo servidor através do barramento RPC."""
        raise NotImplementedError(
            "O servidor gerenciado por RPC intercepta as chamadas nativamente."
        )

    def send_reply(
        self,
        reply: bytes,
        request_id: int,
        obj_ref: str,
        method_id: str,
    ) -> str:
        """Gera e retorna a mensagem de resposta empacotada em formato externo JSON."""
        reply_msg = Message(1, request_id, obj_ref, method_id, reply)
        return reply_msg.serialize()
