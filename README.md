# PRÁCTICA: CALCULADORA DISTRIBUIDA CLIENTE-SERVIDOR
## Resumen Completo

---

## Descripción del Proyecto

Esta práctica implementa una **aplicación Cliente-Servidor en Java** que funciona como una calculadora matemática remota utilizando sockets TCP.

### Características principales:
- ✓ Comunicación bidireccional entre cliente y servidor
- ✓ Envío de datos en formato estructurado: `"numero1;operacion;numero2"`
- ✓ Soporte de operaciones: suma (+), resta (-), multiplicación (*), división (/)
- ✓ Manejo de errores: división por cero
- ✓ Conexiones múltiples (el servidor puede atender varios clientes secuencialmente)
- ✓ Uso de Sockets TCP en Java

---

## Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `server.java` | Servidor que escucha conexiones y procesa cálculos |
| `client.java` | Cliente que se conecta al servidor y envía operaciones |
| `ANALISIS_TEORICO.md` | Respuestas detalladas a las preguntas teóricas |
| `INSTRUCCIONES.md` | Guía paso a paso para compilar y ejecutar |
| `README.md` | Este archivo |

---

## Arquitectura de la Solución

### Server (servidor.java)

**Puerto:** 5500  
**Patrón:** Accept → Process → Send → Close

```
Inicio
  ↓
Crear ServerSocket en puerto 5500
  ↓
┌─ BUCLE INFINITO ─────────────────┐
│                                   │
├─ Esperar conexión (accept)       │
├─ Leer datos del cliente          │
├─ Parsear formato: "num1;op;num2"│
├─ Validar y procesar operación    │
├─ Enviar resultado o error        │
├─ Cerrar conexión con cliente     │
│                                   │
└─ Volver a esperar nueva conexión─┘
```

**Pseudocódigo:**
```
serverSocket = new ServerSocket(5500)
while true:
    socket = serverSocket.accept()  // BLOQUEA hasta que llega cliente
    lectura = new BufferedReader(socket)
    escritura = new PrintWriter(socket)
    
    datos = lectura.readLine()  // BLOQUEA hasta recibir datos
    [numero1, operacion, numero2] = parsear(datos)
    
    resultado = calcular(numero1, operacion, numero2)
    escritura.println(resultado)
    socket.close()
```

### Client (client.java)

**Conexión:** localhost:5500  
**Patrón:** Connect → Send → Receive → Close

```
Inicio
  ↓
Solicitar números y operación al usuario
  ↓
Empaquetar en formato: "numero1;operacion;numero2"
  ↓
Conectar con servidor (localhost:5500)  [BLOQUEA]
  ↓
Enviar solicitud
  ↓
Esperar respuesta  [BLOQUEA]
  ↓
Mostrar resultado
  ↓
Cerrar conexión
  ↓
Fin
```

**Pseudocódigo:**
```
numero1 = input("Ingrese primer número")
operacion = input("Ingrese operación")
numero2 = input("Ingrese segundo número")

mensaje = numero1 + ";" + operacion + ";" + numero2

try:
    socket = new Socket("localhost", 5500)  // BLOQUEA
    escritura = new PrintWriter(socket)
    lectura = new BufferedReader(socket)
    
    escritura.println(mensaje)
    respuesta = lectura.readLine()  // BLOQUEA
    
    print("Resultado: " + respuesta)
    socket.close()
    
except ConnectException:
    print("No se puede conectar. Servidor no está ejecutándose")
```

---

## Formato de Datos

### Solicitud del Cliente al Servidor
```
Formato: "numero1;operacion;numero2"

Ejemplos:
"15;+;30"     → suma
"100;-;25"    → resta
"6;*;7"       → multiplicación
"20;/;4"      → división
"10;/;0"      → error (división por cero)
```

### Respuesta del Servidor al Cliente
```
"45"                          → resultado (suma)
"75"                          → resultado (resta)
"42"                          → resultado (multiplicación)
"5.0"                         → resultado (división)
"ERROR: Division por cero"    → error
"ERROR: Operación no válida"  → error (operador incorrecto)
```

---

## Flujo de Ejecución Completo

```
PASO 1: COMPILACIÓN
┌──────────────────────────────┐
│ javac server.java            │ → server.class
│ javac client.java            │ → client.class
└──────────────────────────────┘

PASO 2: EJECUCIÓN DEL SERVIDOR
┌──────────────────────────────┐
│ Terminal 1:                  │
│ $ java server                │
│                              │
│ Servidor iniciado            │
│ en puerto 5500               │
│ Esperando conexiones...      │
└──────────────────────────────┘

PASO 3: EJECUCIÓN DEL CLIENTE
┌──────────────────────────────┐
│ Terminal 2:                  │
│ $ java client                │
│                              │
│ Ingrese el primer número: 15 │
│ Ingrese la operación: +      │
│ Ingrese el segundo número: 30│
│                              │
│ Enviando: 15;+;30            │
│ Respuesta del servidor: 45   │
└──────────────────────────────┘

PASO 4: RESULTADO EN SERVIDOR
┌──────────────────────────────┐
│ Terminal 1 (Servidor):       │
│                              │
│ Cliente conectado desde:     │
│ 127.0.0.1                    │
│ Datos recibidos: 15;+;30    │
│ Resultado enviado: 45        │
│ Conexión cerrada.            │
│                              │
│ Esperando conexiones...      │
└──────────────────────────────┘
```

---

## Preguntas Teóricas Respondidas

### ❓ Pregunta 1: Excepción cuando servidor no está ejecutándose
**Respuesta:** `java.net.ConnectException: Connection refused`

Se captura en el cliente con:
```java
catch (ConnectException e) {
    System.out.println("ERROR: No se puede conectar al servidor");
}
```

### ❓ Pregunta 2: Líneas que bloquean la ejecución
**Respuesta:** Tres líneas principales:

1. **Servidor (línea 21):** `servidorSocket.accept();`
   - Bloquea esperando una conexión de cliente
   
2. **Cliente (línea 18):** `socket = new Socket(HOST, PUERTO);`
   - Bloquea intentando conectarse al servidor
   
3. **Cliente (línea 41):** `entrada.readLine();`
   - Bloquea esperando la respuesta del servidor

### ❓ Pregunta 3: Cambios para ejecutar en red WiFi
**Respuesta:** Cambiar `localhost` por la IP del servidor

```java
// DE:
private static final String HOST = "localhost";

// A:
private static final String HOST = "192.168.x.x"; // IP real del servidor
```

Pasos:
1. En servidor: obtener IP con `ipconfig`
2. En cliente: reemplazar `localhost` con esa IP
3. Verificar conectividad: `ping 192.168.x.x`

---

## Manejo de Excepciones

| Excepción | Causa | Solución |
|-----------|-------|----------|
| `ConnectException` | Servidor no está ejecutándose | Ejecutar el servidor primero |
| `BindException` | Puerto ya está en uso | Cambiar puerto o cerrar otro programa |
| `NumberFormatException` | Números inválidos en datos | Enviar números enteros válidos |
| `IOException` | Error de comunicación de red | Verificar conexión de red |

---

## Casos de Uso Ejemplificados

### Caso 1: Operación Normal (Suma)
```
Cliente: "25;+;75"
Servidor: Calcula 25 + 75 = 100
Respuesta: "100"
```

### Caso 2: Operación Normal (División)
```
Cliente: "100;/;4"
Servidor: Calcula 100 / 4 = 25.0
Respuesta: "25.0"
```

### Caso 3: Error - División por Cero
```
Cliente: "50;/;0"
Servidor: Detecta división por cero
Respuesta: "ERROR: Division por cero"
```

### Caso 4: Error - Operación Inválida
```
Cliente: "30;#;10"
Servidor: Detecta # no es válido
Respuesta: "ERROR: Operación no válida. Use: +, -, *, /"
```

---

## Conceptos de Red Implementados

✓ **Sockets TCP:** Comunicación confiable basada en conexión  
✓ **Puertos:** El servidor escucha en puerto 5500  
✓ **Conexiones bloqueantes:** Las operaciones de red bloquean hasta completarse  
✓ **Serialización de datos:** Formato delimitado con `;`  
✓ **Manejo de conexiones:** Aceptar, procesar, cerrar  
✓ **Streams de entrada/salida:** BufferedReader y PrintWriter para comunicación  

---

## Mejoras Futuras Posibles

- [ ] Manejar conexiones concurrentes con Threads
- [ ] Implementar protocolo más robusto (JSON, XML)
- [ ] Agregar autenticación del cliente
- [ ] Implementar operaciones más complejas (potencia, raíz cuadrada)
- [ ] Registrar log de operaciones en archivo
- [ ] Implementar timeout de conexión
- [ ] Cliente gráfico (GUI con Swing)
- [ ] Soporte para números decimales en entrada

---

## Requisitos Cumplidos

✓ Cliente solicita dos números y una operación  
✓ Cliente empaquetar datos en formato legible  
✓ Cliente envía datos mediante Socket TCP  
✓ Cliente recibe e imprime el resultado  
✓ Servidor escucha en puerto predeterminado (5500)  
✓ Servidor parsea y procesa la operación  
✓ Servidor maneja división por cero con mensaje de error  
✓ Identifica líneas bloqueantes  
✓ Explica excepción cuando servidor no corre  
✓ Propone cambios para red WiFi  

---

## Referencias

- Java Documentation: https://docs.oracle.com/javase/tutorial/networking/sockets/
- Java Socket API: https://docs.oracle.com/javase/8/docs/api/java/net/Socket.html
- ServerSocket API: https://docs.oracle.com/javase/8/docs/api/java/net/ServerSocket.html

---

**Última actualización:** 2024  
**Estado:** ✓ Completado

