# EJERCICIO 2: ANÁLISIS TEÓRICO-PRÁCTICO
## Calculadora Distribuida Cliente-Servidor

---

## Pregunta 1: ¿Qué sucede con el cliente si el servidor no está ejecutándose?

### Respuesta:
Si el cliente intenta conectar y el servidor no está ejecutándose, Java lanza una **excepción de tipo `ConnectException`**, que es un subtipo de `IOException`.

### Excepción exacta:
```
java.net.ConnectException: Connection refused (La conexión fue rechazada)
```

### En el código:
En el archivo **client.java**, la línea que genera esta excepción es:
```java
socket = new Socket(HOST, PUERTO);  // Línea ~19
```

Esta línea intenta establecer conexión con el servidor en `localhost:5500`. Si no hay ningún servidor escuchando en ese puerto, la excepción se lanza inmediatamente.

### Manejo en el código:
Se captura específicamente esta excepción:
```java
} catch (ConnectException e) {
    System.out.println("ERROR: No se puede conectar al servidor");
    System.out.println("Tipo de excepción: java.net.ConnectException");
    System.out.println("Mensaje: " + e.getMessage());
    System.out.println("\nAsegúrese de que el servidor está ejecutándose en " + HOST + ":" + PUERTO);
}
```

### Ejemplo de salida en consola:
```
ERROR: No se puede conectar al servidor
Tipo de excepción: java.net.ConnectException
Mensaje: Connection refused: connect
Asegúrese de que el servidor está ejecutándose en localhost:5500
```

---

## Pregunta 2: Identifique la línea que bloquea la ejecución del programa

### Respuesta:
En la aplicación hay **dos líneas que bloquean** la ejecución:

#### 1. En el SERVIDOR (server.java, línea ~21):
```java
Socket socketCliente = servidorSocket.accept();
```
**Efecto:** El servidor se detiene en este punto y espera indefinidamente hasta que un cliente se conecte. Esta es una operación bloqueante que solo continúa cuando llega una conexión.

#### 2. En el CLIENTE (client.java, línea ~18):
```java
socket = new Socket(HOST, PUERTO);
```
**Efecto:** El cliente intenta conectarse al servidor. Si el servidor está disponible, se establece la conexión. Si no está disponible, el cliente bloquea durante algunos segundos antes de lanzar la excepción `ConnectException`.

#### 3. En el CLIENTE (client.java, línea ~41):
```java
String respuesta = entrada.readLine();
```
**Efecto:** Después de enviar la solicitud, el cliente se bloquea esperando la respuesta del servidor. Solo continúa cuando recibe una línea completa de datos.

### Diagrama de flujo bloqueante:

```
SERVIDOR:                          CLIENTE:
┌─────────────────────────┐        ┌──────────────────────────┐
│ Espera conexión         │        │ Intenta conectar         │
│ (BLOQUEADO)             │        │ (BLOQUEADO)              │
│ ↓                       │        │ ↓                        │
│ accept() ◄──────────────┼────────► Socket()                │
│         │               │        │         │                │
│         ├───Connected───┼────────┤◄────────┘                │
│         │               │        │                          │
│ Lee datos               │        │ Envía: "15;+;30"        │
│ (BLOQUEADO)             │        │                          │
│ ↓                       │        │ Espera respuesta         │
│ readLine() ◄────────────┼────────► println()               │
│         │               │        │ readLine() (BLOQUEADO)   │
│         │ (recibe)      │        │ ↓                        │
│         ├───Procesión───┤        │ (esperando...)          │
│         │               │        │                          │
│ Calcula y envía respuesta       │                          │
│         ├──"45"─────────┼────────► Recibe respuesta        │
│         │               │        │ Imprime: "45"           │
│ Cierra conexión         │        │ Cierra conexión         │
└─────────────────────────┘        └──────────────────────────┘
```

---

## Pregunta 3: Cambios necesarios para ejecutar en diferentes notebooks en WiFi del aula

### Respuesta:
Para que dos compañeros ejecuten el cliente en una notebook y el servidor en otra (ambas conectadas al WiFi del aula), se necesarían los siguientes cambios:

#### 1. **Cambiar HOST en el cliente:**

**ANTES (client.java, línea ~15):**
```java
private static final String HOST = "localhost";
```

**DESPUÉS:**
```java
private static final String HOST = "192.168.x.x"; // IP del servidor en la red
```

#### 2. **Obtener la IP del servidor:**
- En Windows (servidor): Abrir consola y ejecutar `ipconfig` para obtener la dirección IPv4 en la red WiFi
- Ejemplo: `192.168.100.15`
- Esta IP debe ser accesible desde la otra notebook en la misma red

#### 3. **Asegurar que el puerto está accesible:**
- El puerto 5500 no debe estar bloqueado por firewall
- En Windows: Permitir que Java atraviese el firewall
- Verificación: `netstat -an | findstr :5500` (en el servidor)

#### 4. **Código completo del cliente modificado:**
```java
public class client {
    // CAMBIO: IP de la notebook del servidor en la red WiFi
    private static final String HOST = "192.168.100.15"; 
    private static final int PUERTO = 5500;
    
    public static void main(String[] args) {
        Socket socket = null;
        
        try {
            // El cliente se conecta a través de la red WiFi
            socket = new Socket(HOST, PUERTO);
            System.out.println("Conectado al servidor en " + HOST + ":" + PUERTO);
            
            // ... resto del código igual
        }
    }
}
```

#### 5. **Pasos a seguir en práctica:**

| Paso | Acción | En qué notebook |
|------|--------|-----------------|
| 1 | Compilar ambos programas: `javac server.java` y `javac client.java` | Ambas |
| 2 | Ejecutar servidor: `java server` | Servidor |
| 3 | Anotar la dirección IPv4 de la red WiFi | Servidor (ver en `ipconfig`) |
| 4 | Reemplazar HOST en client.java con la IP del servidor | Cliente |
| 5 | Compilar de nuevo el cliente | Cliente |
| 6 | Ejecutar cliente: `java client` | Cliente |

#### 6. **Verificación de conectividad:**
```bash
# En la notebook cliente, verificar que puede alcanzar el servidor:
ping 192.168.100.15
```

#### 7. **Consideraciones adicionales:**
- **Firewall:** Si no funciona, desactivar temporalmente el firewall o agregar excepción para Java
- **Misma red:** Ambas notebooks deben estar en la misma red WiFi
- **Puertos dinámicos:** Si 5500 está ocupado, cambiar en ambos archivos
- **Timeout:** El cliente espera ~30 segundos antes de fallar si el servidor no responde

---

## Resumen de líneas bloqueantes en el código:

| Archivo | Línea | Código | Tipo de bloqueo |
|---------|-------|--------|-----------------|
| server.java | ~21 | `servidorSocket.accept()` | Espera conexión de cliente |
| client.java | ~18 | `new Socket(HOST, PUERTO)` | Espera establecer conexión |
| client.java | ~41 | `entrada.readLine()` | Espera respuesta del servidor |

