"""Servidor Broker para arquitetura publicar e assinar em Python."""

import argparse
import socket
import threading

from src.server.services.event_broker import EventBroker
from src.server.services.match_service import MatchService
from src.shared.infra.protocol import EventProtocol


def _handle_client(broker: "MatchEventBroker", connection: socket.socket) -> None:
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break

            message = EventProtocol.parse_message(data.decode("utf-8").strip())
            response = broker.handle_message(connection, message)
            if response is not None:
                connection.sendall(response.encode("utf-8"))
    except (ConnectionResetError, OSError, ValueError):
        pass
    finally:
        for topic in list(broker.subscriptions):
            broker.unsubscribe(topic, connection)


class MatchEventBroker(EventBroker):
    def __init__(self) -> None:
        super().__init__()
        self.match_service = MatchService()

    def handle_message(self, connection: socket.socket, message: dict) -> str | None:
        action = (message.get("action") or "").upper()
        topic = message.get("topic", "match.events")

        if action == "SUBSCRIBE":
            self.subscribe(topic, connection)
            return EventProtocol.build_ack(topic, "SUBSCRIBED", {"subscribers": len(self.subscriptions.get(topic, []))})

        if action == "PUBLISH":
            payload = message.get("payload", {})
            event_type = payload.get("event_type", "evento")

            if event_type == "gol":
                self.match_service.register_goal(payload.get("team", "Time"), payload.get("player", "Jogador"), payload.get("minute", "0'"))
            elif event_type == "cartao":
                self.match_service.register_card(payload.get("team", "Time"), payload.get("player", "Jogador"), payload.get("minute", "0'"))

            published = self.publish(topic, payload)
            return EventProtocol.build_ack(topic, "PUBLISHED", published)

        if action == "QUERY":
            if message.get("query") == "score":
                return EventProtocol.build_ack(topic, "OK", self.match_service.get_score())
            if message.get("query") == "events":
                return EventProtocol.build_ack(topic, "OK", self.match_service.get_events())

        return EventProtocol.build_ack(topic, "UNKNOWN_ACTION", {"message": message})


def run_server(host: str = "127.0.0.1", port: int = 5000) -> None:
    broker = MatchEventBroker()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Servidor broker pronto na porta {port}...")

        while True:
            connection, _ = server_socket.accept()
            thread = threading.Thread(target=_handle_client, args=(broker, connection), daemon=True)
            thread.start()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Broker de eventos do sistema de futebol em Python.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host de escuta do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta de escuta do servidor.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    run_server(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
