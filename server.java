import java.io.*;
import java.net.*;

public class server {
    private static final int PUERTO = 5500;
    
    public static void main(String[] args) {
        ServerSocket servidorSocket = null;
        
        try {
            // Crear el servidor en el puerto 5500
            servidorSocket = new ServerSocket(PUERTO);
            System.out.println("Servidor iniciado en puerto " + PUERTO);
            System.out.println("Esperando conexiones del cliente...\n");
            
            // El servidor acepta conexiones indefinidamente
            while (true) {
                // LINEA QUE BLOQUEA: Esta línea se bloquea hasta que llega una Conexion
                Socket socketCliente = servidorSocket.accept();
                System.out.println("Cliente conectado desde: " + socketCliente.getInetAddress().getHostAddress());
                
                // Crear streams para comunicación
                BufferedReader entrada = new BufferedReader(
                    new InputStreamReader(socketCliente.getInputStream())
                );
                PrintWriter salida = new PrintWriter(
                    new OutputStreamWriter(socketCliente.getOutputStream()),
                    true
                );
                
                // Leer datos del cliente
                String datosRecibidos = entrada.readLine();
                System.out.println("Datos recibidos: " + datosRecibidos);
                
                // Parsear los datos: "numero1;operacion;numero2"
                String[] partes = datosRecibidos.split(";");
                
                if (partes.length != 3) {
                    salida.println("ERROR: Formato incorrecto. Use: numero1;operacion;numero2");
                    socketCliente.close();
                    continue;
                }
                
                try {
                    int numero1 = Integer.parseInt(partes[0].trim());
                    String operacion = partes[1].trim();
                    int numero2 = Integer.parseInt(partes[2].trim());
                    
                    // Realizar la operación
                    double resultado = 0;
                    boolean operacionValida = true;
                    
                    switch (operacion) {
                        case "+":
                            resultado = numero1 + numero2;
                            break;
                        case "-":
                            resultado = numero1 - numero2;
                            break;
                        case "*":
                            resultado = numero1 * numero2;
                            break;
                        case "/":
                            if (numero2 == 0) {
                                salida.println("ERROR: Division por cero");
                                operacionValida = false;
                            } else {
                                resultado = (double) numero1 / numero2;
                            }
                            break;
                        default:
                            salida.println("ERROR: Operacion no valida. Use: +, -, *, /");
                            operacionValida = false;
                    }
                    
                    // Enviar resultado al cliente
                    if (operacionValida) {
                        // Formatear el resultado (entero si no tiene decimales)
                        if (resultado == (long) resultado) {
                            salida.println((long) resultado);
                        } else {
                            salida.println(resultado);
                        }
                        System.out.println("Resultado enviado: " + resultado);
                    }
                    
                } catch (NumberFormatException e) {
                    salida.println("ERROR: Los numeros deben ser enteros validos");
                    System.out.println("Error de formato numerico");
                }
                
                // Cerrar la Conexion con este cliente
                socketCliente.close();
                System.out.println("Conexion cerrada.\n");
            }
            
        } catch (IOException e) {
            System.out.println("Error en el servidor: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (servidorSocket != null) {
                try {
                    servidorSocket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
