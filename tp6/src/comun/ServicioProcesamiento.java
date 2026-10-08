package comun;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

/**
 * Interfaz remota: es el "contrato" que comparten cliente y servidor.
 * - Extiende Remote para marcarla como invocable desde otra JVM.
 * - Cada metodo declara RemoteException, porque cualquier llamada puede fallar por la red.
 */
public interface ServicioProcesamiento extends Remote {

    String NOMBRE = "ServicioProcesamiento"; // nombre con el que se publica en el registro
    int PUERTO_REGISTRO = 1099;

    /** Saludo inicial: permite al servidor registrar que se conecto un cliente. */
    String conectar(String nombreCliente) throws RemoteException;

    /** 1) Procesamiento matematico: promedio, maximo, minimo y desviacion estandar. */
    Estadisticas calcularEstadisticas(double[] numeros) throws RemoteException, DatosInvalidosException;

    /** 2) Validacion de criterios: verifica si un CUIT/CUIL es valido (digito verificador). */
    ResultadoValidacion validarCuit(String cuit) throws RemoteException;

    /** 3) Filtro de contenido: devuelve los textos que coinciden con el patron (expresion regular). */
    List<String> filtrarTextos(String[] textos, String patron) throws RemoteException, DatosInvalidosException;

    /** Extra para pruebas: simula una tarea pesada que tarda N segundos (sirve para probar fallos). */
    String tareaLarga(int segundos) throws RemoteException;
}
