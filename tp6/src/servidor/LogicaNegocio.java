package servidor;

import comun.DatosInvalidosException;
import comun.Estadisticas;
import comun.ResultadoValidacion;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

/**
 * Logica de negocio pura: no sabe nada de RMI ni de la red.
 * Asi queda separada de la capa remota y se podria reutilizar o probar sola.
 */
public class LogicaNegocio {

    public Estadisticas estadisticas(double[] numeros) throws DatosInvalidosException {
        if (numeros == null || numeros.length == 0) {
            throw new DatosInvalidosException("La lista de numeros esta vacia");
        }
        double suma = 0, max = numeros[0], min = numeros[0];
        for (double n : numeros) {
            suma += n;
            max = Math.max(max, n);
            min = Math.min(min, n);
        }
        double promedio = suma / numeros.length;

        double sumaCuadrados = 0;
        for (double n : numeros) {
            sumaCuadrados += (n - promedio) * (n - promedio);
        }
        double desviacion = Math.sqrt(sumaCuadrados / numeros.length); // desviacion poblacional

        return new Estadisticas(numeros.length, promedio, max, min, desviacion);
    }

    /**
     * Valida un CUIT/CUIL argentino:
     * 11 digitos, prefijo valido y digito verificador (modulo 11).
     */
    public ResultadoValidacion validarCuit(String cuit) {
        if (cuit == null) {
            return new ResultadoValidacion(false, "No se ingreso ningun valor");
        }
        String limpio = cuit.replace("-", "").replace(" ", "");

        if (!limpio.matches("\\d{11}")) {
            return new ResultadoValidacion(false, "Debe tener 11 digitos numericos");
        }
        String prefijo = limpio.substring(0, 2);
        if (!List.of("20", "23", "24", "27", "30", "33", "34").contains(prefijo)) {
            return new ResultadoValidacion(false, "Prefijo " + prefijo + " no valido");
        }

        int[] multiplicadores = {5, 4, 3, 2, 7, 6, 5, 4, 3, 2};
        int suma = 0;
        for (int i = 0; i < 10; i++) {
            suma += Character.getNumericValue(limpio.charAt(i)) * multiplicadores[i];
        }
        int verificador = 11 - (suma % 11);
        if (verificador == 11) verificador = 0;
        if (verificador == 10) {
            return new ResultadoValidacion(false, "Combinacion invalida (el digito verificador da 10)");
        }

        int ingresado = Character.getNumericValue(limpio.charAt(10));
        if (ingresado != verificador) {
            return new ResultadoValidacion(false,
                    "Digito verificador incorrecto: se esperaba " + verificador + " y se ingreso " + ingresado);
        }
        return new ResultadoValidacion(true, "CUIT " + limpio.substring(0, 2) + "-"
                + limpio.substring(2, 10) + "-" + limpio.charAt(10) + " correcto");
    }

    /** Devuelve los textos que contienen el patron (regex, sin distinguir mayusculas). */
    public List<String> filtrar(String[] textos, String patron) throws DatosInvalidosException {
        if (textos == null || patron == null || patron.isEmpty()) {
            throw new DatosInvalidosException("Faltan los textos o el patron");
        }
        Pattern p;
        try {
            p = Pattern.compile(patron, Pattern.CASE_INSENSITIVE);
        } catch (PatternSyntaxException e) {
            throw new DatosInvalidosException("Patron invalido: " + e.getDescription());
        }
        List<String> resultado = new ArrayList<>();
        for (String t : textos) {
            if (t != null && p.matcher(t).find()) {
                resultado.add(t);
            }
        }
        return resultado;
    }
}
