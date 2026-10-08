import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/**
 * Convierte una Transaccion a bytes (marshalling) y de bytes a Transaccion (unmarshalling)
 * en dos formatos: JSON (texto) y binario directo (DataOutputStream).
 */
public class ParserMensajes {

    // ===================== FORMATO TEXTO (JSON) =====================

    /** Serializa a JSON: {"id":101,"origen":"NodoA","monto":1500.5,"timestamp":1700000000} */
    public static byte[] aJson(Transaccion t) {
        // Locale.US para que el decimal sea con punto y no con coma
        String json = String.format(Locale.US,
                "{\"id\":%d,\"origen\":\"%s\",\"monto\":%s,\"timestamp\":%d}",
                t.getIdTransaccion(), escapar(t.getOrigen()), Double.toString(t.getMonto()), t.getTimestamp());
        return json.getBytes(StandardCharsets.UTF_8);
    }

    /** Deserializa el JSON generado por aJson (parser simple, solo para esta estructura). */
    public static Transaccion desdeJson(byte[] datos) {
        String json = new String(datos, StandardCharsets.UTF_8).trim();
        int id = Integer.parseInt(valor(json, "id"));
        String origen = valor(json, "origen");
        double monto = Double.parseDouble(valor(json, "monto"));
        long timestamp = Long.parseLong(valor(json, "timestamp"));
        return new Transaccion(id, origen, monto, timestamp);
    }

    // Busca "clave": y devuelve el valor como texto (sin comillas si es string)
    private static String valor(String json, String clave) {
        int i = json.indexOf("\"" + clave + "\"");
        if (i < 0) throw new IllegalArgumentException("Falta el campo " + clave);
        i = json.indexOf(':', i) + 1;
        while (json.charAt(i) == ' ') i++;

        if (json.charAt(i) == '"') {           // es un string
            StringBuilder sb = new StringBuilder();
            for (int j = i + 1; j < json.length(); j++) {
                char c = json.charAt(j);
                if (c == '\\') { sb.append(json.charAt(++j)); continue; }
                if (c == '"') break;
                sb.append(c);
            }
            return sb.toString();
        }
        int fin = i;                           // es un numero
        while (fin < json.length() && json.charAt(fin) != ',' && json.charAt(fin) != '}') fin++;
        return json.substring(i, fin).trim();
    }

    private static String escapar(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    // ===================== FORMATO BINARIO =====================

    /**
     * Empaqueta los campos directamente como bytes.
     * DataOutputStream escribe en big-endian (orden de red), sin importar el procesador.
     * Tamano: 4 (int) + 2 + n (writeUTF: largo + texto) + 8 (double) + 8 (long)
     */
    public static byte[] aBinario(Transaccion t) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        DataOutputStream out = new DataOutputStream(baos);
        out.writeInt(t.getIdTransaccion());
        out.writeUTF(t.getOrigen());
        out.writeDouble(t.getMonto());
        out.writeLong(t.getTimestamp());
        out.flush();
        return baos.toByteArray();
    }

    /** Desempaqueta leyendo los campos en el MISMO orden en que se escribieron. */
    public static Transaccion desdeBinario(byte[] datos) throws IOException {
        DataInputStream in = new DataInputStream(new ByteArrayInputStream(datos));
        int id = in.readInt();
        String origen = in.readUTF();
        double monto = in.readDouble();
        long timestamp = in.readLong();
        return new Transaccion(id, origen, monto, timestamp);
    }
}
