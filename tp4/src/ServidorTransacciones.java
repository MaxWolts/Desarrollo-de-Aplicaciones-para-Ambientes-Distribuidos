import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.EOFException;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * Servidor TCP: recibe las rafagas de transacciones, hace el unmarshalling
 * de cada una y al final de cada rafaga muestra bytes recibidos y tiempo.
 */
public class ServidorTransacciones {

    public static void main(String[] args) throws IOException {
        int puerto = args.length > 0 ? Integer.parseInt(args[0]) : Protocolo.PUERTO;

        try (ServerSocket serverSocket = new ServerSocket(puerto)) {
            System.out.println("[SERVIDOR] Escuchando en el puerto " + puerto + "...");
            while (true) {
                try (Socket socket = serverSocket.accept()) {
                    System.out.println("[SERVIDOR] Cliente conectado: " + socket.getRemoteSocketAddress());
                    atender(socket);
                } catch (IOException e) {
                    System.out.println("[SERVIDOR] Error con el cliente: " + e.getMessage());
                }
            }
        }
    }

    private static void atender(Socket socket) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(socket.getInputStream()));

        long bytes = 0;
        int recibidas = 0;
        long inicio = 0;
        Transaccion primera = null;
        Transaccion ultima = null;

        while (true) {
            byte tipo;
            try {
                tipo = in.readByte();
            } catch (EOFException e) {
                System.out.println("[SERVIDOR] El cliente cerro la conexion.\n");
                return;
            }
            int largo = in.readInt();

            if (tipo == Protocolo.FIN) {
                byte formato = in.readByte(); // que formato termino
                double ms = (System.nanoTime() - inicio) / 1_000_000.0;
                System.out.println("----- Rafaga " + Protocolo.nombre(formato) + " recibida -----");
                System.out.println("  Transacciones deserializadas : " + recibidas);
                System.out.println("  Carga util recibida (bytes)  : " + bytes);
                System.out.printf ("  Tiempo recepcion + unmarshal : %.2f ms%n", ms);
                System.out.println("  Primera: " + primera);
                System.out.println("  Ultima : " + ultima);
                bytes = 0; recibidas = 0; inicio = 0; primera = null;
                continue;
            }

            if (recibidas == 0) inicio = System.nanoTime();

            byte[] payload = new byte[largo];
            in.readFully(payload);
            bytes += largo;

            // Unmarshalling: de bytes a objeto
            Transaccion t = (tipo == Protocolo.JSON)
                    ? ParserMensajes.desdeJson(payload)
                    : ParserMensajes.desdeBinario(payload);

            if (primera == null) primera = t;
            ultima = t;
            recibidas++;
        }
    }
}
