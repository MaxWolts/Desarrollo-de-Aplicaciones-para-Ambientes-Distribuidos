package comun;

import java.io.Serializable;

/** Resultado de una validacion: si es valido y un mensaje explicando por que. */
public class ResultadoValidacion implements Serializable {

    private static final long serialVersionUID = 1L;

    private final boolean valido;
    private final String mensaje;

    public ResultadoValidacion(boolean valido, String mensaje) {
        this.valido = valido;
        this.mensaje = mensaje;
    }

    public boolean isValido() { return valido; }
    public String getMensaje() { return mensaje; }

    @Override
    public String toString() {
        return (valido ? "VALIDO" : "INVALIDO") + " - " + mensaje;
    }
}
