package comun;

/**
 * Excepcion de NEGOCIO (no de red): los datos enviados no son validos.
 * Se diferencia de RemoteException, que indica un problema de comunicacion.
 * Las excepciones son Serializable, asi que viajan del servidor al cliente.
 */
public class DatosInvalidosException extends Exception {

    private static final long serialVersionUID = 1L;

    public DatosInvalidosException(String mensaje) {
        super(mensaje);
    }
}
