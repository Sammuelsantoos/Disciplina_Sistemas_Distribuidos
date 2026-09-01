import socket
import struct
import random
import sys
 
class ReliableUdpReceiver:
    HEADER_FORMAT = "!BI"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    BUFFER_SIZE = 2048
 
    TYPE_DATA = 0
    TYPE_FIN = 1
    TYPE_ACK = 99
 
    def __init__(self, port, loss_rate=0.0):
        self.loss_rate = loss_rate                # prob. de "perder" pacote recebido ou ACK enviado
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", port))
        self.expected_seq = 0
 
    def _send_ack(self, seq, address):
        if random.random() < self.loss_rate:
            print(f"[Receiver] Simulando perda do ACK seq={seq}")
            return
        ack = struct.pack(self.HEADER_FORMAT, self.TYPE_ACK, seq)
        self.sock.sendto(ack, address)
 
    def receive_all(self) -> bytes:
        """Bloqueia até receber uma transmissão completa (até o pacote TYPE_FIN)."""
        data = bytearray()
        print(f"[Receiver] Aguardando dados na porta {self.sock.getsockname()[1]}...")
 
        while True:
            packet, address = self.sock.recvfrom(self.BUFFER_SIZE)
 
            if random.random() < self.loss_rate:
                print("[Receiver] Simulando perda de pacote recebido")
                continue
 
            pkt_type, seq = struct.unpack(self.HEADER_FORMAT, packet[:self.HEADER_SIZE])
            payload = packet[self.HEADER_SIZE:]
 
            if seq == self.expected_seq:
                if pkt_type == self.TYPE_FIN:
                    self._send_ack(seq, address)
                    print("[Receiver] Fim de transmissão recebido.")
                    break
 
                data.extend(payload)
                print(f"[Receiver] Pacote seq={seq} aceito ({len(payload)} bytes)")
                self._send_ack(seq, address)
                self.expected_seq += 1
            else:
                # Pacote duplicado (o ACK anterior deve ter se perdido) ou fora de ordem:
                # reenvia o ACK do último pacote realmente aceito.
                print(f"[Receiver] Pacote inesperado seq={seq} (esperado {self.expected_seq}); reenviando ACK antigo")
                if self.expected_seq > 0:
                    self._send_ack(self.expected_seq - 1, address)
 
        return bytes(data)
 
    def close(self):
        self.sock.close()
 
 
def main():
    if len(sys.argv) < 2:
        print("Uso correto: python reliable_udp_receiver.py <port> [loss_rate]")
        sys.exit(1)
 
    port = int(sys.argv[1])
    loss_rate = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
 
    receiver = ReliableUdpReceiver(port, loss_rate=loss_rate)
    data = receiver.receive_all()
 
    print(f"\n[Receiver] Dados completos recebidos ({len(data)} bytes):")
    print(data.decode(errors="replace"))
 
    receiver.close()
 
 
if __name__ == "__main__":
    main()
 
