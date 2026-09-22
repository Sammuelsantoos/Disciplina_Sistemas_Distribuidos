"""Módulo do servidor central de esportes (LiveSportsServer).

Este módulo coordena o recebimento de comandos via conexões TCP (Admin)
e realiza a difusão de eventos esportivos via UDP Multicast (Viewer).
"""

import argparse
import socket
import threading
import json
from src.server.services import MatchService
from src.server.services import NotificationService


class LiveSportsServer:
    """
    Servidor central que coordena partidas esportivas e transmite eventos em
    tempo real usando conexoes TCP multithreading e canais UDP Multicast.
    """

    def __init__(
        self,
        tcp_host: str = "0.0.0.0",
        tcp_port: int = 5000,
        multicast_group: str = "230.0.0.1",
        multicast_port: int = 6000,
    ):
        """
        Inicializa os sockets de comunicacao do servidor, servicos da aplicacao
        e travas de gerenciamento de conexao.
        """
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
        self.active_connections = []

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        """
        Vincula o socket TCP ao host e porta designados, entra em um loop
        infinito de escuta e gera threads de manipulacao de clientes.
        """
        self.tcp_socket.bind((self.tcp_host, self.tcp_port))
        self.tcp_socket.listen(5)
        print(f"Servidor central escutando requisisoes TCP na porta {self.tcp_port}...")
        print("Módulo Multicast UDP ativado e pronto para envio em segundo plano.")

        try:
            while True:
                client_socket, client_address = self.tcp_socket.accept()
                with self.lock:
                    self.active_connections.append(client_socket)

                client_thread = threading.Thread(
                    target=self.handle_admin_client,
                    args=(client_socket, client_address),
                    daemon=True,
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\nEncerrando a execusao do servidor...")
        finally:
            self._cleanup()

    def handle_admin_client(self, client_socket, client_address) -> None:
        """
        Gerencia o ciclo de vida de um painel administrativo conectado via TCP,
        recebendo requisicoes brutas e entregando respostas codificadas.
        """
        print(f"Novo painel administrativo conectado via TCP: {client_address}")
        buffer = ""
        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break

                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue

                    response = self.process_request(line)
                    reply_bytes = (json.dumps(response) + "\n").encode("utf-8")
                    client_socket.sendall(reply_bytes)
        except ConnectionResetError:
            pass
        finally:
            with self.lock:
                if client_socket in self.active_connections:
                    self.active_connections.remove(client_socket)
            client_socket.close()
            print(f"Painel administrativo {client_address} desconectado.")

    def process_request(self, raw_request: str) -> dict:
        """
        Converte mensagens de texto brutas recebidas em estruturas de dados JSON
        e as roteia para a acao manipuladora correspondente.
        """
        try:
            request_data = json.loads(raw_request)
            action = request_data.get("action")

            if action == "CREATE_MATCH":
                return self._handle_create_match(request_data)
            elif action == "REGISTER_EVENT":
                return self._handle_register_event(request_data)
            else:
                return {"status": "ERROR", "message": "Operasao invalida ou desconhecida"}
        except json.JSONDecodeError:
            return {"status": "ERROR", "message": "Formato de payload invalido"}

    def _handle_create_match(self, data: dict) -> dict:
        """
        Instrui o servico interno de partidas a alocar um novo jogo de futebol
        e transmite uma notificacao para o grupo multicast.
        """
        match_id = data.get("match_id")
        home = data.get("home_team")
        away = data.get("away_team")

        with self.lock:
            try:
                self.match_service.create_match(match_id, home, away)
                print(f"Partida registrada em memoria: {home} x {away}")
            except ValueError as error:
                return {"status": "ERROR", "message": str(error)}

        self.notify_service.send_notification(
            notification_type="NOTIFICACAO",
            message=f"Nova partida iniciada no campeonato: {home} x {away}",
        )
        return {"status": "SUCCESS", "message": "Partida cadastrada com sucesso"}

    def _handle_register_event(self, data: dict) -> dict:
        """
        Encaminha os registros de eventos para a camada de banco de dados,
        calcula dinamicamente as atualizacoes de placar e transmite o ocorrido
        via UDP multicast.
        """
        match_id = data.get("match_id")
        event_id = data.get("event_id")
        event_type = data.get("event_type", "").upper()
        description = data.get("description")
        team = data.get("team")

        with self.lock:
            try:
                self.match_service.register_event(event_id, match_id, event_type, description, team)
                match_obj = self.match_service.get_match(match_id)
                print(f"Novo evento salvo no historico CSV: [{event_type}] {description}")
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
        return {"status": "SUCCESS", "message": "Evento processado e enviado para a rede"}

    def _cleanup(self) -> None:
        """
        Encerra conexoes ativas de forma segura, liberando os escutadores do
        socket TCP principal e os servicos de backend com seguranca.
        """
        print("Fechando conexoes pendentes...")
        with self.lock:
            for sock in self.active_connections:
                sock.close()
        self.tcp_socket.close()
        self.notify_service.close()
        print("Servidor finalizado com sucesso.")


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de linha de comando do servidor."""
    parser = argparse.ArgumentParser(description="Servidor central do sistema esportivo.")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="IP/hostname TCP em que o servidor deve escutar.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Porta TCP do servidor central.",
    )
    parser.add_argument(
        "--multicast-group",
        type=str,
        default="230.0.0.1",
        help="Endereço multicast para notificações em tempo real.",
    )
    parser.add_argument(
        "--multicast-port",
        type=int,
        default=6000,
        help="Porta multicast para notificações em tempo real.",
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
