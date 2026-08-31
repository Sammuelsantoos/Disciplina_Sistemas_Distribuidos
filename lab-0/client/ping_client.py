import sys
import time
import socket

def main():
    if len(sys.argv) != 3:
        print("Uso correto: python ping_client.py <host> <port>")
        sys.exit(1)

    # CORREÇÃO: Pegando os índices corretos dos argumentos da linha de comando
    host = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0) # 1 segundo de timeout

    rtts = []
    packets_lost = 0

    print(f"Enviando 10 pings para {host}:{port} via UDP...\n")

    for sequence_number in range(10):
        send_time = time.time()
        message = f"PING {sequence_number} {send_time}\r\n"
        
        try:
            client_socket.sendto(message.encode(), (host, port))
            reply, server_address = client_socket.recvfrom(1024)
            recv_time = time.time()
            
            rtt = (recv_time - send_time) * 1000
            rtts.append(rtt)
            print(f"Resposta de {server_address}: seq={sequence_number} rtt={rtt:.2f} ms")
            
        except socket.timeout:
            packets_lost += 1
            print(f"Solicitação de ping seq={sequence_number} expirou (Timeout).")
        
        if sequence_number < 9:
            time.sleep(1.0)

    client_socket.close()

    print("\n--- Estatísticas do Ping ---")
    packets_sent = 10
    packets_received = len(rtts)
    loss_percentage = (packets_lost / packets_sent) * 100
    print(f"Pacotes: Enviados = {packets_sent}, Recebidos = {packets_received}, Perdidos = {packets_lost} ({loss_percentage:.1f}% de perda)")
    
    if rtts:
        print(f"RTT Mínimo = {min(rtts):.2f} ms | Máximo = {max(rtts):.2f} ms | Média = {sum(rtts)/len(rtts):.2f} ms")

if __name__ == "__main__":
    main()
