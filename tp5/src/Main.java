import java.util.ArrayList;
import java.util.List;

/**
 * Arma el sistema de actores:
 *  - 1 monitor, 1 procesador y 5 sensores (SPAWN)
 *  - cada sensor envia 100 lecturas al mismo tiempo -> 500 mensajes concurrentes (SEND)
 *  - el procesador actualiza su estado con cada mensaje y al final cambia de comportamiento (BECOME)
 */
public class Main {

    private static final int SENSORES = 5;
    private static final int LECTURAS_POR_SENSOR = 100;

    public static void main(String[] args) {
        int sensores = args.length > 0 ? Integer.parseInt(args[0]) : SENSORES;
        int lecturas = args.length > 1 ? Integer.parseInt(args[1]) : LECTURAS_POR_SENSOR;

        System.out.println("=== Sistema de actores: " + sensores + " sensores x " + lecturas
                + " lecturas = " + (sensores * lecturas) + " mensajes ===\n");

        // 1) CREAR (spawn)
        ActorMonitor monitor = Actor.spawn(new ActorMonitor("Monitor"));
        ActorProcesador procesador = Actor.spawn(new ActorProcesador("Procesador", sensores, monitor));

        List<Actor> todos = new ArrayList<>();
        todos.add(procesador);
        List<ActorSensor> listaSensores = new ArrayList<>();
        for (int i = 1; i <= sensores; i++) {
            ActorSensor s = Actor.spawn(new ActorSensor("Sensor-" + i, i));
            listaSensores.add(s);
            todos.add(s);
        }
        monitor.enviar(new Mensajes.Supervisar(todos));
        System.out.println();

        // 2) ENVIAR (send): se arrancan todos los sensores a la vez
        for (ActorSensor s : listaSensores) {
            s.enviar(new Mensajes.Iniciar(lecturas, procesador));
        }
        // el main termina aca; el programa sigue vivo mientras los actores trabajan
    }
}
