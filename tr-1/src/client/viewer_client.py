import socket
import threading
import json
import struct

class SportsViewerClient:
    """
    Cliente multithreading que escuta eventos de partida em tempo real via UDP Multicast mantendo uma interface interativa de terminal ativa para o usuário.
    """
    def __init__(self, multicast_group: str = "230.0.0.1", multicast_port: int = 6000):
        """
        Inicializa as propriedades do socket multicast e os escutadores em segundo plano.
        """
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.is_running = True
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        """
        Vincula o socket do cliente UDP, entra no grupo de rede Classe D e 
        inicia a thread de escuta em segundo plano.
        """
        self.udp_socket.bind((self.multicast_group, self.multicast_port))
        
        mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
        self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        listener_thread = threading.Thread(target=self._listen_multicast_stream, daemon=True)
        listener_thread.start()
        
        self._run_user_interface()

    def _listen_multicast_stream(self) -> None:
        """
        Thread de execução em segundo plano que bloqueia com a chegada de dados, 
        capturando bytes brutos da rede e decodificando alertas esportivos instantaneamente.
        """
        buffer = ""
        while self.is_running:
            try:
                data, _ = self.udp_socket.recvfrom(2048)
                if not data:
                    continue
                
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    
                    self._display_notification(line)
            except Exception:
                break

    def _display_notification(self, raw_json_line: str) -> None:
        """
        Desempacota os payloads de dados externos recebidos e exibe alertas esportivos 
        na tela do console.
        """
        try:
            payload = json.loads(raw_json_line)
            msg_type = payload.get("tipo", "NOTIFICACAO")
            message = payload.get("mensagem", "")
            
            print(f"\n\r[TRANSMISSAO AO VIVO - {msg_type}] {message}")
            print("\rEscolha uma opcao: ", end="", flush=True)
        except json.JSONDecodeError:
            pass

    def _run_user_interface(self) -> None:
        """
        Thread principal de execução que mantém o menu interativo de comandos 
        para verificações de status do sistema ou saída do grupo.
        """
        print("=== BEM-VINDO A CENTRAL DE ESPORTES EM TEMPO REAL ===")
        print("Conectado com sucesso ao canal de transmissao Multicast.")
        
        try:
            while self.is_running:
                print("\n1. Verificar Canal\n2. Sair do Grupo")
                choice = input("Escolha uma opcao: ").strip()
                
                if choice == "1":
                    print(f"Ouvindo feeds ativos no IP de Classe D: {self.multicast_group}:{self.multicast_port}")
                elif choice == "2":
                    print("Saindo do grupo multicast de torcedores...")
                    self.is_running = False
                else:
                    print("Opcao invalida.")
        except (KeyboardInterrupt, EOFError):
            self.is_running = False
        finally:
            self._close_connection()

    def _close_connection(self) -> None:
        """
        Remove as propriedades de membro do grupo de rede Classe D e 
        libera os recursos do socket UDP de forma limpa.
        """
        try:
            mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
            self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        except Exception:
            pass
        self.udp_socket.close()
        print("Conexao com a central esportiva encerrada.")

if __name__ == "__main__":
    client = SportsViewerClient()
    client.start()
