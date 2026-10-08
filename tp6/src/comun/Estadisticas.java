package comun;

import java.io.Serializable;

/**
 * Resultado del calculo estadistico.
 * Implementa Serializable porque viaja POR VALOR: se copia del servidor al cliente.
 */
public class Estadisticas implements Serializable {

    private static final long serialVersionUID = 1L;

    private final int cantidad;
    private final double promedio;
    private final double maximo;
    private final double minimo;
    private final double desviacionEstandar;

    public Estadisticas(int cantidad, double promedio, double maximo, double minimo, double desviacionEstandar) {
        this.cantidad = cantidad;
        this.promedio = promedio;
        this.maximo = maximo;
        this.minimo = minimo;
        this.desviacionEstandar = desviacionEstandar;
    }

    public int getCantidad() { return cantidad; }
    public double getPromedio() { return promedio; }
    public double getMaximo() { return maximo; }
    public double getMinimo() { return minimo; }
    public double getDesviacionEstandar() { return desviacionEstandar; }

    @Override
    public String toString() {
        return String.format("Cantidad: %d | Promedio: %.4f | Maximo: %.4f | Minimo: %.4f | Desv. estandar: %.4f",
                cantidad, promedio, maximo, minimo, desviacionEstandar);
    }
}
