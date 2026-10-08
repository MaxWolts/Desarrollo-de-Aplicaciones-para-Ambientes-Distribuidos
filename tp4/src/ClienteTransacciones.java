import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Cliente TCP: genera 1000 transacciones simuladas y las envia primero en JSON
 * y despues en binario, midiendo tamano de la carga util y tiempo de
 * serializacion + envio de cada formato.
 */
public class ClienteTransacciones {

    public static void main(String[] args) throws IOException {
        String host = args.length > 0 ? args[0] : "localhost";
        int puerto = args.length > 1 ? Integer.parseInt(args[1]) : Protocolo.PUERTO;

        List<Transaccion> lista = generar(Protocolo.CANTIDAD);

        // "Calentamiento": se serializa una vez sin enviar para que la JVM compile
        // el codigo (JIT) y el primer formato medido no salga perjudicado.
        for (Transaccion t : lista) {
            ParserMensajes.aJson(t);
            ParserMensajes.aBinario(t);
        }

        try (Socket socket = new Socket(host, puerto)) {
            DataOutputStream out = new DataOutputStream(new BufferedOutputStream(socket.getOutputStream()));
            System.out.println("Conectado a " + host + ":" + puerto);
            System.out.println("Enviando " + lista.size() + " transacciones por formato...\n");

            long[] json = enviarRafaga(out, lista, Protocolo.JSON);
            long[] bin = enviarRafaga(out, lista, Protocolo.BINARIO);

            System.out.println("================ RESULTADOS (cliente) ================");
            System.out.printf("%-10s %15s %15s %22s%n", "Formato", "Bytes totales", "Bytes/msg", "Serializ.+envio (ms)");
            System.out.printf("%-10s %15d %15.1f %22.2f%n", "JSON", json[0], json[0] / (double) lista.size(), json[1] / 1e6);
            System.out.printf("%-10s %15d %15.1f %22.2f%n", "Binario", bin[0], bin[0] / (double) lista.size(), bin[1] / 1e6);
            System.out.printf("%nEl binario ocupa un %.1f%% menos que JSON.%n", 100.0 * (json[0] - bin[0]) / json[0]);
        }
    }

    /** Devuelve {bytes de carga util, nanosegundos de serializacion + envio}. */
    private static long[] enviarRafaga(DataOutputStream out, List<Transaccion> lista, byte tipo) throws IOException {
        long bytes = 0;
        long inicio = System.nanoTime();

        for (Transaccion t : lista) {
            // Marshalling: de objeto a bytes
            byte[] payload = (tipo == Protocolo.JSON) ? ParserMensajes.aJson(t) : ParserMensajes.aBinario(t);
            out.writeByte(tipo);
            out.writeInt(payload.length);
            out.write(payload);
            bytes += payload.length;
        }
        // aviso de fin de rafaga
        out.writeByte(Protocolo.FIN);
        out.writeInt(0);
        out.writeByte(tipo);
        out.flush();

        long tiempo = System.nanoTime() - inicio;
        System.out.printf("Rafaga %-7s enviada: %d bytes en %.2f ms%n", Protocolo.nombre(tipo), bytes, tiempo / 1e6);
        return new long[]{bytes, tiempo};
    }

    private static List<Transaccion> generar(int n) {
        String[] nodos = {"NodoA", "NodoB", "NodoC", "SucursalCentro", "SucursalNorte"};
        Random r = new Random(42); // semilla fija para que los resultados sean repetibles
        long base = 1700000000L;
        List<Transaccion> lista = new ArrayList<>();
        for (int i = 1; i <= n; i++) {
            double monto = Math.round(r.nextDouble() * 100000) / 100.0; // 2 decimales
            lista.add(new Transaccion(i, nodos[r.nextInt(nodos.length)], monto, base + i));
        }
        return lista;
    }
}
