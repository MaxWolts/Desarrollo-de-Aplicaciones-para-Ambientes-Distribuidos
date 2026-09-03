package tp2;
import java.util.concurrent.ThreadLocalRandom;

public class ClienteResiliente {

    public static void main(String[] args) {
        ejecutarPeticionConResiliencia();
    }

    public static void ejecutarPeticionConResiliencia() {
        int intento = 1;
        int maxIntentos = 5;
        long baseMs = 1000;
        boolean exito = false;
        
        long tiempoInicio = System.currentTimeMillis();

        while (intento <= maxIntentos) {
            try {
                System.out.println("Realizando intento " + intento + "...");
                // Lógica de comunicación con el servidor (simulada)
                simularLlamadaServidor();
                
                exito = true;
                System.out.println("¡Petición exitosa en el intento " + intento + "!");
                break;

            } catch (Exception e) {
                System.out.println("Fallo en el intento " + intento + ": " + e.getMessage());
                
                if (intento == maxIntentos) {
                    break;
                }

                // Ejercicio 1: Cálculo del tiempo de espera con Jitter
                // Fórmula: (Base * 2^(intento-1)) + Random(0, 500) ms
                long tiempoExponencial = (long) (baseMs * Math.pow(2, intento - 1));
                long jitter = ThreadLocalRandom.current().nextInt(501);
                long tiempoEsperado = tiempoExponencial + jitter;

                System.out.println("Esperando " + tiempoEsperado + " ms antes del siguiente intento...\n");
                try {
                    Thread.sleep(tiempoEsperado);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    System.err.println("El hilo de espera fue interrumpido.");
                }
                
                intento++;
            }
        }

        long tiempoTotal = System.currentTimeMillis() - tiempoInicio;

        // Ejercicio 2: Mostrar Métricas de Resiliencia
        mostrarMetricas(exito, intento, tiempoTotal);
    }

    private static void simularLlamadaServidor() throws Exception {
        // Simula un error aleatorio para probar la resiliencia (falla el 75% de las primeras veces)
        if (Math.random() < 0.75) {
            throw new Exception("Servidor saturado o no disponible");
        }
    }

    private static void mostrarMetricas(boolean exito, int intentosRealizados, long tiempoTotalMs) {
        System.out.println("\n========================================");
        System.out.println("          MÉTRICAS DE RESILIENCIA       ");
        System.out.println("========================================");
        System.out.println("Estado final de la petición : " + (exito ? "Éxito" : "Fallo definitivo"));
        System.out.println("Cantidad de intentos        : " + intentosRealizados);
        System.out.println("Tiempo total transcurrido   : " + tiempoTotalMs + " ms");
        System.out.println("========================================");
    }
}