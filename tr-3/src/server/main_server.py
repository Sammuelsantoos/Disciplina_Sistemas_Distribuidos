"""Servidor TCP que executa o RPC do sistema de eventos esportivos."""

import argparse
import socket

from src.server.services.rpc_service import RPCService


def handle_request(request: str) -> str:
    """Processa a requisição enviada pelo cliente."""
    service = RPCService()
    return service.dispatch(request)


def run_server(host: str = "127.0.0.1", port: int = 5000) -> None:
    """Escuta conexões e atende chamadas RPC."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Servidor pronto na porta {port}...")

        while True:
            connection, _ = server_socket.accept()
            with connection:
                data = connection.recv(4096).decode("utf-8").strip()
                print(f"Requisição recebida: {data}")
                response = handle_request(data)
                connection.sendall(response.encode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Servidor RPC de eventos de futebol em Python.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host de escuta do servidor.")
    parser.add_argument("--port", type=int, default=5000, help="Porta de escuta do servidor.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    run_server(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
