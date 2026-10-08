import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Recibe el resultado final, lo muestra, verifica que no se perdio ningun
 * mensaje y apaga a todos los actores.
 */
public class ActorMonitor extends Actor {

    private List<Actor> supervisados = new ArrayList<>();

    public ActorMonitor(String nombre) {
        super(nombre);
    }

    @Override
    protected void recibir(Object mensaje) {
        if (mensaje instanceof Mensajes.Supervisar) {
            supervisados = ((Mensajes.Supervisar) mensaje).actores;

        } else if (mensaje instanceof Mensajes.Resultado) {
            Mensajes.Resultado r = (Mensajes.Resultado) mensaje;

            System.out.println();
            System.out.println("================= RESULTADO FINAL =================");
            System.out.println("Lecturas procesadas : " + r.procesadas + " / " + r.esperadas + " enviadas");
            System.out.printf ("Promedio final      : %.2f C%n", r.promedio);
            System.out.printf ("Minimo / Maximo     : %.2f C / %.2f C%n", r.minimo, r.maximo);
            System.out.println("Lecturas por sensor :");
            for (Map.Entry<String, Integer> e : new TreeMap<>(r.porSensor).entrySet()) {
                System.out.println("   " + e.getKey() + " -> " + e.getValue());
            }

            // Verificacion: lo procesado tiene que coincidir con lo que los sensores dicen que enviaron
            boolean cantidadOk = r.procesadas == r.esperadas;
            boolean sumaOk = Math.abs(r.sumaProcesada - r.sumaEsperada) < 1e-6;
            System.out.printf ("Suma procesada      : %.2f (esperada %.2f)%n", r.sumaProcesada, r.sumaEsperada);
            System.out.println(cantidadOk && sumaOk
                    ? "VERIFICACION OK: sin mensajes perdidos ni condiciones de carrera"
                    : "ERROR: los valores no coinciden");
            System.out.println("===================================================");
            System.out.println();

            // apaga a todos (incluido el mismo)
            for (Actor a : supervisados) {
                a.enviar(Mensajes.Detener.INSTANCIA);
            }
            enviar(Mensajes.Detener.INSTANCIA);
        }
    }
}
