import java.io.*;
import java.net.*;
import java.util.Scanner;

public class client {
    private static final String HOST = "localhost";
    private static final int PUERTO = 5500;
    
    public static void main(String[] args) {
        Socket socket = null;
        
        try {
            // LINEA QUE BLOQUEA: Esta línea se bloquea hasta que se establece conexión con el servidor
            socket = new Socket(HOST, PUERTO);
            System.out.println("Conectado al servidor en " + HOST + ":" + PUERTO + "\n");
            
            // Crear streams para comunicación
            BufferedReader entrada = new BufferedReader(
                new InputStreamReader(socket.getInputStream())
            );
            PrintWriter salida = new PrintWriter(
                new OutputStreamWriter(socket.getOutputStream()),
                true
            );
            
            // Solicitar datos al usuario
            Scanner scanner = new Scanner(System.in);
            
            System.out.println("=== CALCULADORA DISTRIBUIDA ===");
            System.out.print("Ingrese el primer numero: ");
            int numero1 = scanner.nextInt();
            
            System.out.print("Ingrese la operacion (+, -, *, /): ");
            String operacion = scanner.next();
            
            System.out.print("Ingrese el segundo numero: ");
            int numero2 = scanner.nextInt();
            
            // Empaquetar datos en formato: "numero1;operacion;numero2"
            String mensaje = numero1 + ";" + operacion + ";" + numero2;
            System.out.println("\nEnviando: " + mensaje);
            
            // Enviar datos al servidor
            salida.println(mensaje);
            
            // LINEA QUE BLOQUEA: Esta línea se bloquea esperando la respuesta del servidor
            String respuesta = entrada.readLine();
            System.out.println("Respuesta del servidor: " + respuesta);
            
            scanner.close();
            
        } catch (ConnectException e) {
            // Excepción específica cuando el servidor no está ejecutándose
            System.out.println("ERROR: No se puede conectar al servidor");
            System.out.println("Tipo de excepcion: java.net.ConnectException");
            System.out.println("Mensaje: " + e.getMessage());
            System.out.println("\nAsegurese de que el servidor esta ejecutandose en " + HOST + ":" + PUERTO);
            
        } catch (IOException e) {
            System.out.println("Error de comunicacion: " + e.getMessage());
            e.printStackTrace();
            
        } finally {
            if (socket != null) {
                try {
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
