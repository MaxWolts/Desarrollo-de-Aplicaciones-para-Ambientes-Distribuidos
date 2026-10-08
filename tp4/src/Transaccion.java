/**
 * Estructura de datos que se va a transmitir por la red.
 */
public class Transaccion {

    private final int idTransaccion;   // entero de 32 bits
    private final String origen;       // cadena de texto
    private final double monto;        // flotante de doble precision (64 bits)
    private final long timestamp;      // entero de 64 bits

    public Transaccion(int idTransaccion, String origen, double monto, long timestamp) {
        this.idTransaccion = idTransaccion;
        this.origen = origen;
        this.monto = monto;
        this.timestamp = timestamp;
    }

    public int getIdTransaccion() { return idTransaccion; }
    public String getOrigen() { return origen; }
    public double getMonto() { return monto; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "Transaccion{id=" + idTransaccion + ", origen=" + origen
                + ", monto=" + monto + ", timestamp=" + timestamp + "}";
    }
}
