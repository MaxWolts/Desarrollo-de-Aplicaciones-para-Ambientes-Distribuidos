import java.util.Random;

/**
 * Simula un dispositivo que mide temperatura.
 * Cuando recibe Iniciar, genera N lecturas y se las envia al destino.
 */
public class ActorSensor extends Actor {

    private final Random random;

    public ActorSensor(String nombre, long semilla) {
        super(nombre);
        this.random = new Random(semilla); // semilla fija: resultados repetibles
    }

    @Override
    protected void recibir(Object mensaje) {
        if (mensaje instanceof Mensajes.Iniciar) {
            Mensajes.Iniciar orden = (Mensajes.Iniciar) mensaje;
            double suma = 0;

            for (int i = 1; i <= orden.cantidad; i++) {
                // temperatura entre 15 y 35 grados, con 2 decimales
                double valor = Math.round((15 + random.nextDouble() * 20) * 100) / 100.0;
                suma += valor;
                orden.destino.enviar(new Mensajes.Lectura(getNombre(), i, valor)); // SEND
            }
            // al terminar avisa cuantas mando y cuanto sumaban, para verificar
            orden.destino.enviar(new Mensajes.FinSensor(getNombre(), orden.cantidad, suma));
        }
    }
}
