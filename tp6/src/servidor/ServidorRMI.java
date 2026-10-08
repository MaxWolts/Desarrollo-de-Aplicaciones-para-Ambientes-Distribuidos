package servidor;

import comun.ServicioProcesamiento;

import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

/**
 * Levanta el RMI Registry y publica el servicio bajo un nombre.
 *
 * Uso: java -cp out servidor.ServidorRMI [puerto]
 */
public class ServidorRMI {

    public static void main(String[] args) {
        int puerto = args.length > 0 ? Integer.parseInt(args[0]) : ServicioProcesamiento.PUERTO_REGISTRO;

        try {
            // 1) Crear el registro de nombres dentro de esta misma JVM
            Registry registry = LocateRegistry.createRegistry(puerto);

            // 2) Crear y exportar el objeto remoto
            ServicioProcesamientoImpl servicio = new ServicioProcesamientoImpl();

            // 3) Publicarlo con un nombre para que los clientes lo encuentren
            registry.rebind(ServicioProcesamiento.NOMBRE, servicio);

            System.out.println("==============================================");
            System.out.println(" Servidor RMI listo");
            System.out.println(" Registro en el puerto " + puerto);
            System.out.println(" Servicio publicado como '" + ServicioProcesamiento.NOMBRE + "'");
            System.out.println(" Esperando clientes... (Ctrl+C para terminar)");
            System.out.println("==============================================");
            // El hilo del registro mantiene viva la JVM
        } catch (RemoteException e) {
            System.err.println("No se pudo iniciar el servidor: " + e.getMessage());
            System.err.println("Puede que el puerto " + puerto + " ya este en uso.");
        }
    }
}
