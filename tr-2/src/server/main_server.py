"""Módulo do servidor central de esportes (LiveSportsServer).

Este módulo coordena o recebimento de comandos e consultas de forma síncrona
utilizando chamadas de procedimento remoto (RPC) e payloads estruturados em JSON.
"""

import argparse
from xmlrpc.server import SimpleXMLRPCServer
import json
import threading

from src.server.services.match_service import MatchService
from src.server.services.notify_service import NotificationService
from src.shared.infra.protocol import RequestReplyProtocol


class LiveSportsServer:
    """Servidor central que coordena partidas esportivas e eventos via RPC."""

    def __init__(
        self,
        tcp_host: str = "0.0.0.0",
        tcp_port: int = 5000,
        multicast_group: str = "230.0.0.1",
        multicast_port: int = 6000,
    ) -> None:
        """Inicializa as propriedades do servidor de chamadas e travas concorrentes."""
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port

        self.match_service = MatchService()
        self.notify_service = NotificationService(
            multicast_group=self.multicast_group,
            multicast_port=self.multicast_port,
        )

        self.lock = threading.Lock()

    def execute_action(self, payload_json: str) -> str:
        """Ponto de entrada RPC unificado que realiza o unmarshaling de strings JSON."""
        try:
            request_data = json.loads(payload_json)

            method = request_data.get("methodId", "").strip().lower()
            arguments_str = request_data.get("arguments", "{}")

            args_dict = json.loads(arguments_str)

            req_id = request_data.get("requestId", 1)
            obj_ref = request_data.get("objectReference", "CentralSportsService")

            if method == "create_match":
                raw_result = self._handle_create_match(args_dict)
            elif method == "register_event":
                raw_result = self._handle_register_event(args_dict)
            elif method == "get_score":
                raw_result = self._handle_get_score(args_dict)
            elif method == "list_matches":
                raw_result = self._handle_list_matches()
            elif method == "get_events":
                raw_result = self._handle_get_events(args_dict)
            else:
                raw_result = {
                    "status": "ERROR", "message": f"Método {method} inválido ou desconhecido"
                }


            reply_bytes = json.dumps(raw_result).encode("utf-8")

            local_protocol = RequestReplyProtocol()
            return local_protocol.send_reply(
                reply=reply_bytes,
                request_id=req_id,
                obj_ref=obj_ref,
                method_id=method
            )

        except json.JSONDecodeError:
            error_payload = json.dumps(
                {"status": "ERROR", "message": "Formato de payload inválido"}
            ).encode("utf-8")
            local_protocol = RequestReplyProtocol()
            return local_protocol.send_reply(
                reply=error_payload,
                request_id=0,
                obj_ref="CentralSportsService",
                method_id="error"
            )

    def _handle_create_match(self, data: dict) -> dict:
        """Processa remotamente a criação de partidas de forma thread-safe."""
        match_id = data.get("match_id")
        home = data.get("home_team")
        away = data.get("away_team")

        with self.lock:
            try:
                self.match_service.create_match(match_id, home, away)
                print(f"Partida registrada em memória: {home} x {away}")
            except ValueError as error:
                return {"status": "ERROR", "message": str(error)}

        self.notify_service.send_notification(
            notification_type="NOTIFICACAO",
            message=f"Nova partida iniciada no campeonato: {home} x {away}",
        )
        return {"status": "SUCCESS", "message": "Partida cadastrada com sucesso"}

    def _handle_register_event(self, data: dict) -> dict:
        """Processa remotamente o registro de gols ou advertências de forma thread-safe."""
        match_id = data.get("match_id")
        event_id = data.get("event_id")
        event_type = data.get("event_type", "").upper()
        description = data.get("description")
        team = data.get("team")

        with self.lock:
            try:
                self.match_service.register_event(event_id, match_id, event_type, description, team)
                match_obj = self.match_service.get_match(match_id)
                print(f"Novo evento salvo: [{event_type}] {description}")
            except (KeyError, ValueError) as error:
                return {"status": "ERROR", "message": str(error)}

        alert_label = "ALERTA" if event_type == "GOL" else "ATUALIZACAO"
        display_message = (
            f"[{event_type}] {match_obj.home_team} {match_obj.home_score} x "
            f"{match_obj.away_score} {match_obj.away_team} - {description}"
        )

        self.notify_service.send_notification(
            notification_type=alert_label,
            message=display_message,
        )
        return {"status": "SUCCESS", "message": "Evento processado com sucesso"}

    def _handle_get_score(self, data: dict) -> dict:
        """Consulta e retorna o placar consolidado síncronamente via RPC."""
        match_id = data.get("match_id")
        with self.lock:
            try:
                match_obj = self.match_service.get_match(match_id)
                display_message = f"{
                    match_obj.home_team
                } {match_obj.home_score} x {match_obj.away_score} {match_obj.away_team}"
                return {"status": "SUCCESS", "message": display_message}
            except (KeyError, ValueError) as error:
                return {"status": "ERROR", "message": str(error)}

    def _handle_list_matches(self) -> dict:
        """Retorna o estado de todos os jogos ativos em andamento na central."""
        with self.lock:
            # pylint: disable=protected-access
            matches_summary = {
                m_id: f"{m_obj.home_team} {m_obj.home_score} x {m_obj.away_score} {m_obj.away_team}"
                for m_id, m_obj in self.match_service._matches.items()
            }
            return {"status": "SUCCESS", "matches": matches_summary}

    def _handle_get_events(self, data: dict) -> dict:
        """Consulta e retorna o histórico de lances de uma partida via RPC."""
        match_id = data.get("match_id")
        with self.lock:
            try:
                events_list = self.match_service.get_events(match_id)
                events_summary = [
                    f"[{evt.event_type}] {
                        getattr(evt, 'team', getattr(evt, 'player', ''))
                    } - {evt.description}"
                    for evt in events_list
                ]
                return {"status": "SUCCESS", "events": events_summary}
            except (KeyError, ValueError) as error:
                return {"status": "ERROR", "message": str(error)}


    def start(self) -> None:
        """Ativa o loop contínuo do servidor RPC sem expor Sockets na aplicação."""
        server = SimpleXMLRPCServer((self.tcp_host, self.tcp_port), allow_none=True)
        server.register_instance(self)
        print(f"Servidor central RPC escutando requisições na porta {self.tcp_port}...")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrando a execução do servidor...")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de linha de comando do servidor."""
    parser = argparse.ArgumentParser(description="Servidor central RPC do sistema esportivo.")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="IP/hostname em que o servidor RPC deve escutar.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Porta de escuta do servidor RPC.",
    )
    parser.add_argument(
        "--multicast-group",
        type=str,
        default="230.0.0.1",
        help="Endereço de configuração para notificações.",
    )
    parser.add_argument(
        "--multicast-port",
        type=int,
        default=6000,
        help="Porta de configuração para notificações.",
    )
    return parser


def main(argv=None) -> int:
    """Executa o servidor usando argumentos de linha de comando."""
    args = build_parser().parse_args(argv)
    server = LiveSportsServer(
        tcp_host=args.host,
        tcp_port=args.port,
        multicast_group=args.multicast_group,
        multicast_port=args.multicast_port,
    )
    server.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
