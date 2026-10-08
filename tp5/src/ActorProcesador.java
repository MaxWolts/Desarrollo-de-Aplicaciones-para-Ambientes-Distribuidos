import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Nodo central: recibe las lecturas en su buzon FIFO y lleva un contador
 * y un promedio acumulado.
 *
 * Todo el estado es PRIVADO y solo lo modifica el hilo de este actor,
 * por eso no hace falta synchronized ni locks: nunca hay dos hilos tocandolo a la vez.
 */
public class ActorProcesador extends Actor {

    // ----- estado privado (no hay getters ni setters) -----
    private int contador = 0;
    private double suma = 0;
    private double minimo = Double.MAX_VALUE;
    private double maximo = -Double.MAX_VALUE;
    private final Map<String, Integer> porSensor = new HashMap<>();

    private int sensoresTerminados = 0;
    private int esperadas = 0;
    private double sumaEsperada = 0;

    private final int sensoresTotales;
    private final Actor monitor;

    // comportamiento actual: se cambia con become()
    private Consumer<Object> comportamiento;

    public ActorProcesador(String nombre, int sensoresTotales, Actor monitor) {
        super(nombre);
        this.sensoresTotales = sensoresTotales;
        this.monitor = monitor;
        this.comportamiento = this::procesando; // comportamiento inicial
    }

    @Override
    protected void recibir(Object mensaje) {
        comportamiento.accept(mensaje);
    }

    /** DESIGNAR (become): define como se va a atender el SIGUIENTE mensaje. */
    private void become(Consumer<Object> nuevo, String descripcion) {
        System.out.println("[BECOME] " + getNombre() + " cambia su comportamiento a: " + descripcion);
        this.comportamiento = nuevo;
    }

    // ----- Comportamiento 1: procesando lecturas -----
    private void procesando(Object mensaje) {
        if (mensaje instanceof Mensajes.Lectura) {
            Mensajes.Lectura l = (Mensajes.Lectura) mensaje;

            // actualiza el estado para el proximo mensaje de la cola
            contador++;
            suma += l.valor;
            minimo = Math.min(minimo, l.valor);
            maximo = Math.max(maximo, l.valor);
            porSensor.merge(l.sensor, 1, Integer::sum);

            System.out.printf("[%s] #%03d <- %-8s lectura %3d: %5.2f C | promedio acumulado = %.2f C%n",
                    Thread.currentThread().getName(), contador, l.sensor, l.secuencia, l.valor, suma / contador);

        } else if (mensaje instanceof Mensajes.FinSensor) {
            Mensajes.FinSensor fin = (Mensajes.FinSensor) mensaje;
            sensoresTerminados++;
            esperadas += fin.cantidadEnviada;
            sumaEsperada += fin.sumaEnviada;
            System.out.println("[" + getNombre() + "] " + fin.sensor + " termino de enviar ("
                    + fin.cantidadEnviada + " lecturas)");

            if (sensoresTerminados == sensoresTotales) {
                become(this::cerrado, "CERRADO (no acepta mas lecturas)");
                monitor.enviar(new Mensajes.Resultado(contador, suma / contador, minimo, maximo,
                        esperadas, suma, sumaEsperada, new HashMap<>(porSensor)));
            }
        }
    }

    // ----- Comportamiento 2: ya cerro el lote -----
    private void cerrado(Object mensaje) {
        if (mensaje instanceof Mensajes.Lectura) {
            System.out.println("[" + getNombre() + "] Lectura descartada: el lote ya fue cerrado");
        }
    }
}
