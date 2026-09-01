import socket
import struct
import random
import sys
import time
 
class ReliableUdpSender:
    HEADER_FORMAT = "!BI"                       # 1 byte (tipo) + 4 bytes (seq)
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAX_PAYLOAD = 1000                            # bytes de dados por pacote
 
    TYPE_DATA = 0
    TYPE_FIN = 1                                  # sinaliza fim da transmissão
    TYPE_ACK = 99
 
    def __init__(self, host, port, timeout=1.0, max_retries=5, loss_rate=0.0):
        self.address = (host, port)
        self.timeout = timeout
        self.max_retries = max_retries
        self.loss_rate = loss_rate                # prob. de o remetente "perder" um envio
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.seq = 0
 
    def _make_packet(self, pkt_type, seq, payload=b""):
        return struct.pack(self.HEADER_FORMAT, pkt_type, seq) + payload
 
    def _send_with_simulated_loss(self, packet, seq):
        if random.random() < self.loss_rate:
            print(f"[Sender] Simulando perda do pacote seq={seq}")
            return
        self.sock.sendto(packet, self.address)
 
    def _send_reliable(self, pkt_type, payload=b""):
        seq = self.seq
        packet = self._make_packet(pkt_type, seq, payload)
        attempts = 0
 
        while attempts <= self.max_retries:
            self._send_with_simulated_loss(packet, seq)
            try:
                ack, _ = self.sock.recvfrom(self.HEADER_SIZE)
                ack_type, ack_seq = struct.unpack(self.HEADER_FORMAT, ack[:self.HEADER_SIZE])
                if ack_type == self.TYPE_ACK and ack_seq == seq:
                    self.seq += 1
                    return True
                # ACK de outra sequência (ex.: duplicado antigo) -> ignora e continua esperando
            except socket.timeout:
                attempts += 1
                print(f"[Sender] Timeout esperando ACK seq={seq}, retransmitindo (tentativa {attempts}/{self.max_retries})")
 
        print(f"[Sender] Falha ao entregar pacote seq={seq} após {self.max_retries} tentativas.")
        return False
 
    def send(self, data: bytes) -> bool:
        """Envia 'data' de forma confiável, fragmentando em pacotes de até MAX_PAYLOAD bytes."""
        if not data:
            data = b""
        for i in range(0, max(len(data), 1), self.MAX_PAYLOAD):
            chunk = data[i:i + self.MAX_PAYLOAD]
            if not self._send_reliable(self.TYPE_DATA, chunk):
                return False
            if len(data) == 0:
                break
        return self._send_reliable(self.TYPE_FIN)
 
    def close(self):
        self.sock.close()
 
 
def main():
    if len(sys.argv) < 4:
        print("Uso correto: python reliable_udp_sender.py <host> <port> <mensagem> [loss_rate]")
        sys.exit(1)
 
    host = sys.argv[1]
    port = int(sys.argv[2])
    message = sys.argv[3]
    loss_rate = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
 
    sender = ReliableUdpSender(host, port, timeout=1.0, max_retries=5, loss_rate=loss_rate)
 
    start = time.time()
    ok = sender.send(message.encode())
    elapsed = time.time() - start
 
    if ok:
        print(f"\n[Sender] Mensagem entregue com sucesso em {elapsed:.2f}s.")
    else:
        print(f"\n[Sender] Falha ao entregar a mensagem.")
 
    sender.close()
 
 
if __name__ == "__main__":
    main()
