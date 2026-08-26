import java.io.*;
import java.net.*;
import java.util.*;

/*
 * Servidor para processar as requisições de Ping sobre UDP.
 */
public class PingServer {
    private static final double LOSS_RATE = 0.3;
    private static final int AVERAGE_DELAY = 100; // milissegundos
    private static DatagramSocket socket;

    public static void main(String[] args) throws Exception {
        // Verificar o argumento da linha de comando.
        if (args.length != 1) {
            System.out.println("Uso obrigatorio: java PingServer <porta>");
            return;
        }
        
        int port = Integer.parseInt(args[0]);
        Random random = new Random();
        socket = new DatagramSocket(port);
        
        System.out.println("PingServer rodando na porta " + port + "...");

        while (true) {
            // Buffer para receber o pacote de entrada
            byte[] buffer = new byte[1024];
            DatagramPacket request = new DatagramPacket(buffer, buffer.length);
            
            // Bloqueia até que um pacote UDP chegue
            socket.receive(request);
            
            // Imprimir os dados recebidos
            printData(request);
            
            // Simular perda de pacotes
            if (random.nextDouble() < LOSS_RATE) {
                System.out.println("   -> Resposta nao enviada (Perda simulada).");
                continue;
            }
            
            // Simular o atraso da rede de forma correta
            int delay = (int) (random.nextDouble() * 2 * AVERAGE_DELAY);
            Thread.sleep(delay);
            
            // Enviar resposta (Echo)
            InetAddress clientHost = request.getAddress();
            int clientPort = request.getPort();
            byte[] buf = request.getData();
            int length = request.getLength(); // Pega o tamanho real dos dados enviados
            
            DatagramPacket reply = new DatagramPacket(buf, length, clientHost, clientPort);
            socket.send(reply);
            System.out.println("   -> Resposta enviada com atraso de " + delay + "ms.");
        }
    }

    /*
     * Imprimir o dado de Ping recebido
     */
    private static void printData(DatagramPacket request) throws Exception {
        byte[] buf = request.getData();
        // Lendo apenas a quantidade exata de bytes recebidos
        ByteArrayInputStream bais = new ByteArrayInputStream(buf, 0, request.getLength());
        InputStreamReader isr = new InputStreamReader(bais);
        BufferedReader br = new BufferedReader(isr);
        
        String line = br.readLine();
        System.out.println("Recebido de " + request.getAddress().getHostAddress() + ":" + request.getPort() + " -> " + line);
    }
}
