import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * Todos los mensajes del sistema.
 * Son INMUTABLES (clases final con atributos final): una vez creados nadie los
 * puede modificar, asi que se pueden pasar entre hilos sin riesgo.
 */
public final class Mensajes {

    private Mensajes() {}

    /** Orden para que un sensor empiece a generar lecturas. */
    public static final class Iniciar {
        public final int cantidad;
        public final Actor destino;

        public Iniciar(int cantidad, Actor destino) {
            this.cantidad = cantidad;
            this.destino = destino;
        }
    }

    /** Una lectura de temperatura enviada por un sensor. */
    public static final class Lectura {
        public final String sensor;
        public final int secuencia;
        public final double valor;

        public Lectura(String sensor, int secuencia, double valor) {
            this.sensor = sensor;
            this.secuencia = secuencia;
            this.valor = valor;
        }
    }

    /** Aviso de que un sensor termino. Lleva lo que envio para poder verificar. */
    public static final class FinSensor {
        public final String sensor;
        public final int cantidadEnviada;
        public final double sumaEnviada;

        public FinSensor(String sensor, int cantidadEnviada, double sumaEnviada) {
            this.sensor = sensor;
            this.cantidadEnviada = cantidadEnviada;
            this.sumaEnviada = sumaEnviada;
        }
    }

    /** Resultado final que el procesador le manda al monitor. */
    public static final class Resultado {
        public final int procesadas;
        public final double promedio;
        public final double minimo;
        public final double maximo;
        public final int esperadas;
        public final double sumaProcesada;
        public final double sumaEsperada;
        public final Map<String, Integer> porSensor;

        public Resultado(int procesadas, double promedio, double minimo, double maximo,
                         int esperadas, double sumaProcesada, double sumaEsperada,
                         Map<String, Integer> porSensor) {
            this.procesadas = procesadas;
            this.promedio = promedio;
            this.minimo = minimo;
            this.maximo = maximo;
            this.esperadas = esperadas;
            this.sumaProcesada = sumaProcesada;
            this.sumaEsperada = sumaEsperada;
            this.porSensor = Collections.unmodifiableMap(porSensor); // copia de solo lectura
        }
    }

    /** Le pasa al monitor la lista de actores que tiene que apagar al final. */
    public static final class Supervisar {
        public final List<Actor> actores;

        public Supervisar(List<Actor> actores) {
            this.actores = Collections.unmodifiableList(actores);
        }
    }

    /** "Pildora venenosa": el actor que la recibe termina su ciclo. */
    public static final class Detener {
        public static final Detener INSTANCIA = new Detener();
        private Detener() {}
    }
}
