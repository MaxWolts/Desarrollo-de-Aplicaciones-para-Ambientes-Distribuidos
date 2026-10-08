/**
 * Constantes que comparten cliente y servidor.
 *
 * Como TCP es un flujo de bytes sin limites de mensaje, cada mensaje se envia con
 * un pequeno encabezado (framing):
 *
 *   [1 byte: tipo] [4 bytes: largo del payload] [payload]
 *
 * El tipo FIN indica que termino la rafaga de un formato.
 */
public class Protocolo {
    public static final int PUERTO = 5000;
    public static final int CANTIDAD = 1000;

    public static final byte JSON = 1;
    public static final byte BINARIO = 2;
    public static final byte FIN = 0;

    public static String nombre(byte tipo) {
        return tipo == JSON ? "JSON" : tipo == BINARIO ? "Binario" : "FIN";
    }
}
