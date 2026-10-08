import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

/**
 * Clase base de todos los actores.
 *
 * Cada actor tiene:
 *  - un buzon (mailbox) FIFO propio donde otros actores dejan mensajes,
 *  - un hilo propio que saca los mensajes de a uno y los procesa,
 *  - estado privado que solo toca su propio hilo.
 *
 * La unica forma de interactuar con un actor es enviarle un mensaje (enviar()),
 * que es asincronico: se deja en el buzon y el emisor sigue de largo.
 */
public abstract class Actor implements Runnable {

    private final String nombre;
    private final BlockingQueue<Object> buzon = new LinkedBlockingQueue<>();
    private boolean activo = true; // solo lo lee y modifica el hilo del propio actor

    protected Actor(String nombre) {
        this.nombre = nombre;
    }

    /** CREAR (spawn): le asigna un hilo al actor y lo pone a escuchar su buzon. */
    public static <T extends Actor> T spawn(T actor) {
        new Thread(actor, actor.getNombre()).start();
        System.out.println("[SPAWN] Actor creado: " + actor.getNombre());
        return actor;
    }

    /** ENVIAR (send): deja el mensaje en el buzon y retorna enseguida (no bloquea). */
    public final void enviar(Object mensaje) {
        buzon.offer(mensaje);
    }

    public final String getNombre() {
        return nombre;
    }

    @Override
    public final void run() {
        try {
            while (activo) {
                Object mensaje = buzon.take(); // espera si el buzon esta vacio
                if (mensaje instanceof Mensajes.Detener) {
                    activo = false;
                } else {
                    recibir(mensaje); // se procesa UN mensaje a la vez
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        System.out.println("[STOP] " + nombre + " finalizado");
    }

    /** Lo que hace el actor con cada mensaje. Lo define cada tipo de actor. */
    protected abstract void recibir(Object mensaje);
}
