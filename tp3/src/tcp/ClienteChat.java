import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

/**
 * Cliente de chat TCP.
 * Usa un hilo para escuchar los mensajes del servidor y el hilo principal
 * para leer lo que escribe el usuario por teclado.
 */
public class ClienteChat {

    public static void main(String[] args) {
        String host = args.length > 0 ? args[0] : "localhost";
        int puerto = args.length > 1 ? Integer.parseInt(args[1]) : 5000;

        try (Socket socket = new Socket(host, puerto);
             BufferedReader entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter salida = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader teclado = new BufferedReader(new InputStreamReader(System.in))) {

            System.out.println("Conectado a " + host + ":" + puerto + " (escriba /salir para terminar)");

            // Hilo receptor: imprime todo lo que llega del servidor
            Thread receptor = new Thread(() -> {
                try {
                    String msg;
                    while ((msg = entrada.readLine()) != null) {
                        System.out.println(msg);
                    }
                } catch (IOException e) {
                    // el socket se cerro
                }
                System.out.println("Conexion con el servidor finalizada.");
            });
            receptor.setDaemon(true);
            receptor.start();

            String linea;
            while ((linea = teclado.readLine()) != null) {
                salida.println(linea);
                if (linea.equalsIgnoreCase("/salir")) {
                    break;
                }
            }
        } catch (IOException e) {
            System.err.println("No se pudo conectar al servidor: " + e.getMessage());
        }
    }
}
