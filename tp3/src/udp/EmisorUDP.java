import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

/**
 * Emisor UDP: envia una alerta de telemetria cada cierto intervalo.
 * No hay conexion previa, cada mensaje es un datagrama independiente.
 */
public class EmisorUDP {

    public static void main(String[] args) throws Exception {
        String host = args.length > 0 ? args[0] : "localhost";
        int puerto = args.length > 1 ? Integer.parseInt(args[1]) : 6000;
        int intervaloMs = args.length > 2 ? Integer.parseInt(args[2]) : 2000;

        InetAddress destino = InetAddress.getByName(host);
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("HH:mm:ss");

        try (DatagramSocket socket = new DatagramSocket()) {
            int contador = 1;
            while (true) {
                double temperatura = 20 + Math.random() * 60; // dato simulado
                String mensaje = String.format("ALERTA #%d | %s | temperatura=%.1f C",
                        contador, LocalTime.now().format(fmt), temperatura);

                byte[] datos = mensaje.getBytes("UTF-8");
                DatagramPacket paquete = new DatagramPacket(datos, datos.length, destino, puerto);
                socket.send(paquete); // "disparar y olvidar": no hay confirmacion de llegada

                System.out.println("[EMISOR] Enviado: " + mensaje);
                contador++;
                Thread.sleep(intervaloMs);
            }
        }
    }
}
