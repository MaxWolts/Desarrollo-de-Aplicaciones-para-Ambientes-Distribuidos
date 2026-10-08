import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Servidor de chat TCP multihilo.
 * El hilo principal solo acepta conexiones y por cada cliente
 * crea un hilo (ManejadorCliente) que atiende su comunicacion.
 */
public class ServidorChat {

    private static final int PUERTO = 5000;

    // Lista de clientes conectados. Es thread-safe porque la usan varios hilos a la vez.
    private static final Set<ManejadorCliente> clientes = ConcurrentHashMap.newKeySet();

    public static void main(String[] args) {
        int puerto = args.length > 0 ? Integer.parseInt(args[0]) : PUERTO;
        System.out.println("[SERVIDOR] Escuchando en el puerto " + puerto + "...");

        try (ServerSocket serverSocket = new ServerSocket(puerto)) {
            while (true) {
                // accept() bloquea hasta que llega un cliente y devuelve un Socket exclusivo para el
                Socket socket = serverSocket.accept();
                System.out.println("[SERVIDOR] Nueva conexion desde " + socket.getRemoteSocketAddress());

                ManejadorCliente manejador = new ManejadorCliente(socket);
                clientes.add(manejador);
                new Thread(manejador).start(); // se delega el cliente a un hilo independiente
            }
        } catch (IOException e) {
            System.err.println("[SERVIDOR] Error: " + e.getMessage());
        }
    }

    /** Reenvia el mensaje a todos los clientes menos al que lo envio. */
    static void broadcast(String mensaje, ManejadorCliente emisor) {
        for (ManejadorCliente c : clientes) {
            if (c != emisor) {
                c.enviar(mensaje);
            }
        }
    }

    static void eliminar(ManejadorCliente c) {
        clientes.remove(c);
        System.out.println("[SERVIDOR] Clientes conectados: " + clientes.size());
    }

    /** Hilo que atiende a un unico cliente. */
    static class ManejadorCliente implements Runnable {
        private final Socket socket;
        private PrintWriter salida;
        private String nombre;

        ManejadorCliente(Socket socket) {
            this.socket = socket;
        }

        @Override
        public void run() {
            try (BufferedReader entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {
                salida = new PrintWriter(socket.getOutputStream(), true);

                salida.println("Ingrese su nombre:");
                nombre = entrada.readLine();
                if (nombre == null || nombre.isBlank()) {
                    nombre = "Anonimo-" + socket.getPort();
                }
                System.out.println("[SERVIDOR] " + nombre + " se unio al chat");
                broadcast(">> " + nombre + " se unio al chat", this);

                String linea;
                // readLine() devuelve null cuando el cliente cierra la conexion
                while ((linea = entrada.readLine()) != null) {
                    if (linea.equalsIgnoreCase("/salir")) {
                        break;
                    }
                    System.out.println("[" + nombre + "] " + linea);
                    broadcast("[" + nombre + "] " + linea, this);
                }
            } catch (IOException e) {
                // desconexion abrupta (ej: se cerro la consola del cliente)
                System.out.println("[SERVIDOR] Conexion perdida con " + nombre);
            } finally {
                desconectar();
            }
        }

        void enviar(String mensaje) {
            if (salida != null) {
                salida.println(mensaje);
            }
        }

        private void desconectar() {
            eliminar(this);
            broadcast(">> " + nombre + " salio del chat", this);
            try {
                socket.close(); // se cierra solo el socket de este cliente, el servidor sigue funcionando
            } catch (IOException ignored) {
            }
            System.out.println("[SERVIDOR] " + nombre + " desconectado");
        }
    }
}
