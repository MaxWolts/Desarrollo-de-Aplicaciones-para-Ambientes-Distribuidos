import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketTimeoutException;

/**
 * Receptor UDP con timeout.
 * Si en 5 segundos no llega ningun datagrama, receive() lanza
 * SocketTimeoutException: se registra una advertencia y se sigue escuchando.
 */
public class ReceptorUDP {

    private static final int TIMEOUT_MS = 5000;

    public static void main(String[] args) {
        int puerto = args.length > 0 ? Integer.parseInt(args[0]) : 6000;
        byte[] buffer = new byte[1024];

        try (DatagramSocket socket = new DatagramSocket(puerto)) {
            socket.setSoTimeout(TIMEOUT_MS);
            System.out.println("[RECEPTOR] Escuchando datagramas en el puerto " + puerto
                    + " (timeout " + TIMEOUT_MS / 1000 + " s)");

            while (true) {
                DatagramPacket paquete = new DatagramPacket(buffer, buffer.length);
                try {
                    socket.receive(paquete); // bloquea como maximo 5 segundos
                    String mensaje = new String(paquete.getData(), 0, paquete.getLength(), "UTF-8");
                    System.out.println("[RECEPTOR] De " + paquete.getAddress().getHostAddress()
                            + ":" + paquete.getPort() + " -> " + mensaje);
                } catch (SocketTimeoutException e) {
                    System.out.println("[ADVERTENCIA] No se recibieron datagramas en los ultimos "
                            + TIMEOUT_MS / 1000 + " segundos. Sigo escuchando...");
                }
            }
        } catch (IOException e) {
            System.err.println("[RECEPTOR] Error: " + e.getMessage());
        }
    }
}
