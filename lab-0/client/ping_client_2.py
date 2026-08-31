# Exercício 2: Modificar o programa de modo que ele envie exatamente 1 Ping por segundo, corrigindo atrasos de resposta ou timeout.

import sys
import time
import socket

def main():
    if len(sys.argv) != 3:
        print("Uso correto: python ping_client.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.99) 

    rtts = []
    packets_lost = 0

    print(f"Enviando 10 pings espaçados rigidamente em 1 segundo para {host}:{port}...\n")

    base_time = time.time()

    for sequence_number in range(10):
        scheduled_send_time = base_time + (sequence_number * 1.0)
        
        now = time.time()
        if scheduled_send_time > now:
            time.sleep(scheduled_send_time - now)
            
        send_time = time.time()
        message = f"PING {sequence_number} {send_time}\r\n"
        
        try:
            client_socket.sendto(message.encode(), (host, port))
            reply, server_address = client_socket.recvfrom(1024)
            recv_time = time.time()
            
            rtt = (recv_time - send_time) * 1000
            rtts.append(rtt)
            print(f"[{sequence_number}] Resposta de {server_address}: rtt={rtt:.2f} ms")
            
        except socket.timeout:
            packets_lost += 1
            print(f"[{sequence_number}] Solicitação de ping expirou (Timeout).")

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
