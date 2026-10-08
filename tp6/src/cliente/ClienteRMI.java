package cliente;

import comun.DatosInvalidosException;
import comun.Estadisticas;
import comun.ResultadoValidacion;
import comun.ServicioProcesamiento;

import java.rmi.ConnectException;
import java.rmi.NoSuchObjectException;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.UnmarshalException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * Cliente por consola. Obtiene el stub del servicio en el registro y
 * llama a sus metodos como si fueran locales.
 *
 * Uso: java -cp out cliente.ClienteRMI [host] [puerto]
 */
public class ClienteRMI {

    private static String host;
    private static int puerto;
    private static ServicioProcesamiento servicio; // stub (proxy) del objeto remoto
    private static final Scanner sc = new Scanner(System.in);

    /** Una llamada remota cualquiera, para manejar los errores en un solo lugar. */
    interface LlamadaRemota {
        void ejecutar() throws RemoteException, DatosInvalidosException;
    }

    /** Tiempo maximo de espera de una respuesta (ms). Sin esto el cliente puede quedar bloqueado para siempre. */
    private static final String TIMEOUT_RESPUESTA_MS = "30000";

    public static void main(String[] args) {
        // Timeouts de RMI: se configuran antes de usar cualquier clase de RMI
        System.setProperty("sun.rmi.transport.tcp.responseTimeout", TIMEOUT_RESPUESTA_MS);
        System.setProperty("sun.rmi.transport.connectionTimeout", "5000");

        host = args.length > 0 ? args[0] : "localhost";
        puerto = args.length > 1 ? Integer.parseInt(args[1]) : ServicioProcesamiento.PUERTO_REGISTRO;

        if (!conectar()) {
            return;
        }

        while (true) {
            System.out.println();
            System.out.println("========= MENU =========");
            System.out.println("1) Estadisticas de una lista de numeros");
            System.out.println("2) Validar CUIT/CUIL");
            System.out.println("3) Filtrar textos por patron");
            System.out.println("4) Tarea larga (para probar fallos)");
            System.out.println("5) Reconectar");
            System.out.println("0) Salir");
            System.out.print("Opcion: ");
            String op = sc.nextLine().trim();

            switch (op) {
                case "1": invocar(ClienteRMI::opcionEstadisticas); break;
                case "2": invocar(ClienteRMI::opcionCuit); break;
                case "3": invocar(ClienteRMI::opcionFiltro); break;
                case "4": invocar(ClienteRMI::opcionTareaLarga); break;
                case "5": conectar(); break;
                case "0": System.out.println("Chau!"); return;
                default: System.out.println("Opcion invalida");
            }
        }
    }

    /** Busca el servicio en el registro (lookup) y obtiene el stub. */
    private static boolean conectar() {
        try {
            Registry registry = LocateRegistry.getRegistry(host, puerto);
            servicio = (ServicioProcesamiento) registry.lookup(ServicioProcesamiento.NOMBRE);
            String usuario = System.getProperty("user.name", "cliente");
            System.out.println(servicio.conectar(usuario));
            return true;
        } catch (NotBoundException e) {
            System.out.println("[ERROR] El registro no tiene publicado '" + ServicioProcesamiento.NOMBRE + "'");
        } catch (RemoteException e) {
            System.out.println("[ERROR] No se pudo contactar al registro en " + host + ":" + puerto
                    + " -> " + e.getClass().getSimpleName());
        }
        return false;
    }

    /** Ejecuta una llamada remota y traduce cada tipo de fallo a un mensaje claro. */
    private static void invocar(LlamadaRemota llamada) {
        if (servicio == null && !conectar()) {
            return;
        }
        try {
            llamada.ejecutar();
        } catch (DatosInvalidosException e) {
            // error de negocio: la llamada llego bien, pero los datos no sirven
            System.out.println("[DATOS INVALIDOS] " + e.getMessage());
        } catch (ConnectException e) {
            // no se pudo abrir la conexion: el servidor no esta corriendo
            System.out.println("[FALLO] ConnectException: el servidor no esta disponible. Pruebe la opcion 5 mas tarde.");
        } catch (UnmarshalException e) {
            // la conexion se corto (o vencio el timeout) mientras se esperaba la respuesta
            String causa = e.getCause() instanceof java.net.SocketTimeoutException
                    ? "el servidor no respondio en " + Integer.parseInt(TIMEOUT_RESPUESTA_MS) / 1000 + " s (timeout)"
                    : "se perdio la conexion durante la ejecucion";
            System.out.println("[FALLO] UnmarshalException: " + causa + ".");
            System.out.println("        No se sabe si el metodo llego a ejecutarse en el servidor.");
        } catch (NoSuchObjectException e) {
            // el servidor se reinicio y el stub viejo ya no sirve
            System.out.println("[FALLO] NoSuchObjectException: la referencia remota ya no existe. Reconectando...");
            conectar();
        } catch (RemoteException e) {
            System.out.println("[FALLO] " + e.getClass().getSimpleName() + ": " + e.getMessage());
        }
    }

    // ----------------- opciones del menu -----------------

    private static void opcionEstadisticas() throws RemoteException, DatosInvalidosException {
        System.out.print("Numeros separados por espacio o coma: ");
        String[] partes = sc.nextLine().trim().split("[\\s,;]+");
        List<Double> lista = new ArrayList<>();
        for (String p : partes) {
            if (p.isEmpty()) continue;
            try {
                lista.add(Double.parseDouble(p));
            } catch (NumberFormatException e) {
                System.out.println("Se ignora '" + p + "' (no es un numero)");
            }
        }
        double[] numeros = lista.stream().mapToDouble(Double::doubleValue).toArray();

        Estadisticas e = servicio.calcularEstadisticas(numeros); // llamada remota transparente
        System.out.println("Resultado -> " + e);
    }

    private static void opcionCuit() throws RemoteException {
        System.out.print("CUIT/CUIL (ej: 20-12345678-6): ");
        ResultadoValidacion r = servicio.validarCuit(sc.nextLine());
        System.out.println("Resultado -> " + r);
    }

    private static void opcionFiltro() throws RemoteException, DatosInvalidosException {
        System.out.print("Textos separados por ';': ");
        String[] textos = sc.nextLine().split(";");
        for (int i = 0; i < textos.length; i++) textos[i] = textos[i].trim();
        System.out.print("Patron de busqueda (texto o expresion regular): ");
        String patron = sc.nextLine();

        List<String> r = servicio.filtrarTextos(textos, patron);
        System.out.println("Coincidencias (" + r.size() + "): " + r);
    }

    private static void opcionTareaLarga() throws RemoteException {
        System.out.print("Segundos que dura la tarea: ");
        int seg;
        try {
            seg = Integer.parseInt(sc.nextLine().trim());
        } catch (NumberFormatException e) {
            seg = 10;
        }
        System.out.println("Esperando respuesta del servidor (el cliente queda bloqueado)...");
        System.out.println("Resultado -> " + servicio.tareaLarga(seg));
    }
}
