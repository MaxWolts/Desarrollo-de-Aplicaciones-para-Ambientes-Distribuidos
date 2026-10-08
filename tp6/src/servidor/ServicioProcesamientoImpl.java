package servidor;

import comun.DatosInvalidosException;
import comun.Estadisticas;
import comun.ResultadoValidacion;
import comun.ServicioProcesamiento;

import java.rmi.RemoteException;
import java.rmi.server.RemoteServer;
import java.rmi.server.ServerNotActiveException;
import java.rmi.server.UnicastRemoteObject;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;

/**
 * Objeto remoto (servant). Extender UnicastRemoteObject lo "exporta":
 * queda escuchando llamadas y RMI genera el stub para los clientes.
 *
 * Esta clase solo se encarga de la parte remota y de la trazabilidad;
 * el calculo real lo hace LogicaNegocio.
 */
public class ServicioProcesamientoImpl extends UnicastRemoteObject implements ServicioProcesamiento {

    private static final long serialVersionUID = 1L;
    private static final DateTimeFormatter HORA = DateTimeFormatter.ofPattern("HH:mm:ss");

    private final LogicaNegocio logica = new LogicaNegocio();

    public ServicioProcesamientoImpl() throws RemoteException {
        super();
    }

    @Override
    public String conectar(String nombreCliente) {
        log("CONEXION de cliente '" + nombreCliente + "'");
        return "Bienvenido " + nombreCliente + ", conectado al " + NOMBRE;
    }

    @Override
    public Estadisticas calcularEstadisticas(double[] numeros) throws DatosInvalidosException {
        log("calcularEstadisticas(" + Arrays.toString(numeros) + ")");
        Estadisticas e = logica.estadisticas(numeros);
        log("  -> " + e);
        return e;
    }

    @Override
    public ResultadoValidacion validarCuit(String cuit) {
        log("validarCuit(\"" + cuit + "\")");
        ResultadoValidacion r = logica.validarCuit(cuit);
        log("  -> " + r);
        return r;
    }

    @Override
    public List<String> filtrarTextos(String[] textos, String patron) throws DatosInvalidosException {
        log("filtrarTextos(" + (textos == null ? 0 : textos.length) + " textos, patron=\"" + patron + "\")");
        List<String> r = logica.filtrar(textos, patron);
        log("  -> " + r.size() + " coincidencias");
        return r;
    }

    @Override
    public String tareaLarga(int segundos) {
        log("tareaLarga(" + segundos + " s) iniciada");
        try {
            Thread.sleep(segundos * 1000L);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        log("tareaLarga finalizada");
        return "Tarea de " + segundos + " segundos completada";
    }

    /** Traza en consola: hora, IP del cliente que llamo, hilo y operacion. */
    private void log(String texto) {
        String cliente;
        try {
            cliente = RemoteServer.getClientHost(); // IP del cliente que hizo la llamada
        } catch (ServerNotActiveException e) {
            cliente = "local";
        }
        System.out.printf("[%s] [cliente %s] [%s] %s%n",
                LocalTime.now().format(HORA), cliente, Thread.currentThread().getName(), texto);
    }
}
