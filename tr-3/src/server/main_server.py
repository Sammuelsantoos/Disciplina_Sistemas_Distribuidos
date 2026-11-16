"""Servidor Broker para arquitetura publicar e assinar (Pub/Sub) em Python.

Este módulo gerencia inscrições de clientes em tópicos e coordena a publicação
e consulta de eventos esportivos de forma thread-safe com persistência em CSV.
"""

import argparse
import socket
import threading

from src.server.services.event_broker import EventBroker
from src.server.services.match_service import MatchService
from src.shared.infra.protocol import EventProtocol


def _handle_client(broker: "MatchEventBroker", connection: socket.socket) -> None:
    """Gerencia a conexão individual de um cliente TCP de forma contínua."""
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break

            raw_text = data.decode("utf-8").strip()
            if not raw_text:
                continue

            # Caso cheguem múltiplas mensagens coladas no buffer TCP
            for line in raw_text.splitlines():
                message = EventProtocol.parse_message(line)
                response = broker.handle_message(connection, message)
                if response is not None:
                    connection.sendall((response + "\n").encode("utf-8"))

    except (ConnectionResetError, OSError, ValueError) as error:
        print(f"Conexão encerrada ou erro de protocolo: {error}")
    finally:
        for topic in list(broker.subscriptions):
            broker.unsubscribe(topic, connection)
        connection.close()


class MatchEventBroker(EventBroker):
    """Broker especializado em eventos esportivos que integra Pub/Sub e MatchService."""

    def __init__(self, storage_path: str = "src/data/event.csv") -> None:
        """Inicializa o broker, o serviço de partidas e a trava de concorrência."""
        super().__init__()
        self.match_service = MatchService(storage_path=storage_path)
        self.lock = threading.Lock()

    def handle_message(self, connection: socket.socket, message: dict) -> str | None:
        """Roteia as ações SUBSCRIBE, PUBLISH e QUERY recebidas dos clientes."""
        action = (message.get("action") or "").upper()
        topic = message.get("topic", "match.events")

        if action == "SUBSCRIBE":
            return self._handle_subscribe(connection, topic)

        if action == "PUBLISH":
            return self._handle_publish(topic, message.get("payload", {}))

        if action == "QUERY":
            return self._handle_query(topic, message)

        return EventProtocol.build_ack(
            topic, "UNKNOWN_ACTION", {"message": f"Ação '{action}' desconhecida"}
        )

    def _handle_subscribe(self, connection: socket.socket, topic: str) -> str:
        """Inscreve um cliente em um tópico específico."""
        with self.lock:
            self.subscribe(topic, connection)
            total_subs = len(self.subscriptions.get(topic, []))
        print(f"Novo assinante no tópico '{topic}' (Total: {total_subs})")
        return EventProtocol.build_ack(
            topic, "SUBSCRIBED", {"subscribers": total_subs}
        )

    def _handle_publish(self, topic: str, payload: dict) -> str:
        """Processa a publicação de novas partidas ou eventos, salva no CSV e notifica."""
        event_type = str(payload.get("event_type", "")).upper()
        match_id = payload.get("match_id", 1)

        with self.lock:
            try:
                # 1. Criação de nova partida via Pub/Sub
                if event_type == "CREATE_MATCH":
                    home = payload.get("home_team")
                    away = payload.get("away_team")
                    self.match_service.create_match(match_id, home, away)
                    print(f"Partida cadastrada: [{match_id}] {home} x {away}")

                # 2. Registro de eventos esportivos (GOL, CARD, END)
                elif event_type in {"GOL", "CARD", "END"}:
                    event_id = payload.get("event_id") or self._next_event_id()
                    team = payload.get("team")
                    player = payload.get("player")
                    minute = payload.get("minute")

                    # Monta a descrição automática se não vier pronta no payload
                    description = payload.get("description")
                    if not description:
                        if event_type == "GOL":
                            description = f"{player or 'Jogador'} marcou para {team} aos {minute or '0'}'."
                        elif event_type == "CARD":
                            description = f"Cartão para {player or team} aos {minute or '0'}'."
                        else:
                            description = "Partida encerrada."

                    # Para CARD, o MatchService espera o jogador no parâmetro 'team' (context_value)
                    context_val = player if (event_type == "CARD" and player) else team

                    self.match_service.register_event(
                        event_id=event_id,
                        match_id=match_id,
                        event_type=event_type,
                        description=description,
                        team=context_val,
                    )

                    match_obj = self.match_service.get_match(match_id)
                    payload["description"] = description
                    payload["home_score"] = match_obj.home_score
                    payload["away_score"] = match_obj.away_score
                    print(f"Evento salvo no CSV: [{event_type}] {description}")

            except (KeyError, ValueError) as error:
                return EventProtocol.build_ack(topic, "ERROR", {"message": str(error)})

        # Dispara a mensagem para todos os assinantes do tópico
        published = self.publish(topic, payload)
        return EventProtocol.build_ack(topic, "PUBLISHED", published)

    def _handle_query(self, topic: str, message: dict) -> str:
        """Responde a consultas síncronas de placar, eventos ou lista de jogos."""
        query_type = (message.get("query") or "").lower()
        match_id = message.get("match_id", 1)

        with self.lock:
            try:
                if query_type == "score":
                    match_obj = self.match_service.get_match(match_id)
                    result = {
                        "match_id": match_obj.match_id,
                        "home_team": match_obj.home_team,
                        "away_team": match_obj.away_team,
                        "home_score": match_obj.home_score,
                        "away_score": match_obj.away_score,
                    }
                    return EventProtocol.build_ack(topic, "OK", result)

                if query_type == "events":
                    events_list = self.match_service.get_events(match_id)
                    serialized_events = [evt.to_dict() for evt in events_list]
                    return EventProtocol.build_ack(topic, "OK", serialized_events)

                if query_type == "matches":
                    # pylint: disable=protected-access
                    matches_summary = {
                        m_id: f"{m.home_team} {m.home_score} x {m.away_score} {m.away_team}"
                        for m_id, m in self.match_service._matches.items()
                    }
                    return EventProtocol.build_ack(topic, "OK", matches_summary)

            except (KeyError, ValueError) as error:
                return EventProtocol.build_ack(topic, "ERROR", {"message": str(error)})

        return EventProtocol.build_ack(
            topic, "UNKNOWN_QUERY", {"message": f"Consulta '{query_type}' inválida"}
        )

    def _next_event_id(self) -> int:
        """Gera um ID sequencial seguro baseado nos eventos já carregados."""
        # pylint: disable=protected-access
        return max(self.match_service._event_ids, default=0) + 1


def run_server(
    host: str = "127.0.0.1", port: int = 5000, storage_path: str = "src/data/event.csv"
) -> None:
    """Inicia o socket TCP do Broker e aceita conexões concorrentes."""
    broker = MatchEventBroker(storage_path=storage_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Servidor Broker Pub/Sub escutando em {host}:{port}...")

        try:
            while True:
                connection, _ = server_socket.accept()
                thread = threading.Thread(
                    target=_handle_client, args=(broker, connection), daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            print("\nEncerrando a execução do Broker...")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de linha de comando do Broker."""
    parser = argparse.ArgumentParser(
        description="Broker de eventos do sistema de futebol em Python."
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host de escuta do servidor."
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Porta de escuta do servidor."
    )
    parser.add_argument(
        "--storage",
        type=str,
        default="src/data/event.csv",
        help="Caminho do arquivo CSV para persistência.",
    )
    return parser


def main(argv=None) -> int:
    """Ponto de entrada principal do servidor Broker."""
    args = build_parser().parse_args(argv)
    run_server(host=args.host, port=args.port, storage_path=args.storage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
