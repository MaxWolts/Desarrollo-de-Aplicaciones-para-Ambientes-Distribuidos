# INSTRUCCIONES DE COMPILACIÓN Y EJECUCIÓN

## Prerequisitos
- Java Development Kit (JDK) instalado (versión 8 o superior)
- Dos terminales (una para el servidor, otra para el cliente)

---

## Paso 1: Compilar los programas

Abra una terminal en el directorio del proyecto y ejecute:

```bash
javac server.java
javac client.java
```

Esto generará dos archivos `.class`:
- `server.class`
- `client.class`

---

## Paso 2: Ejecutar el Servidor

En la primera terminal, ejecute:

```bash
java server
```

Verá una salida como esta:
```
Servidor iniciado en puerto 5500
Esperando conexiones del cliente...
```

**⚠️ IMPORTANTE:** El servidor debe estar ejecutándose ANTES de que intente conectar el cliente.

---

## Paso 3: Ejecutar el Cliente

Abra una SEGUNDA terminal en el mismo directorio y ejecute:

```bash
java client
```

El cliente le pedirá que ingrese los datos:

```
=== CALCULADORA DISTRIBUIDA ===
Ingrese el primer número: 15
Ingrese la operación (+, -, *, /): +
Ingrese el segundo número: 30

Enviando: 15;+;30
Respuesta del servidor: 45
```

---

## Ejemplos de Uso

### Ejemplo 1: Suma
```
Ingrese el primer número: 100
Ingrese la operación (+, -, *, /): +
Ingrese el segundo número: 50
Enviando: 100;+;50
Respuesta del servidor: 150
```

### Ejemplo 2: División
```
Ingrese el primer número: 20
Ingrese la operación (+, -, *, /): /
Ingrese el segundo número: 4
Enviando: 20;/;4
Respuesta del servidor: 5.0
```

### Ejemplo 3: División por cero (Error)
```
Ingrese el primer número: 10
Ingrese la operación (+, -, *, /): /
Ingrese el segundo número: 0
Enviando: 10;/;0
Respuesta del servidor: ERROR: Division por cero
```

### Ejemplo 4: Operación inválida
```
Ingrese el primer número: 5
Ingrese la operación (+, -, *, /): %
Ingrese el segundo número: 3
Enviando: 5;%;3
Respuesta del servidor: ERROR: Operación no válida. Use: +, -, *, /
```

---

## Salida esperada en el Servidor

```
Servidor iniciado en puerto 5500
Esperando conexiones del cliente...

Cliente conectado desde: 127.0.0.1
Datos recibidos: 15;+;30
Resultado enviado: 45
Conexión cerrada.

Cliente conectado desde: 127.0.0.1
Datos recibidos: 20;/;4
Resultado enviado: 5.0
Conexión cerrada.

Cliente conectado desde: 127.0.0.1
Datos recibidos: 10;/;0
ERROR: Division por cero
Conexión cerrada.
```

---

## Solución de Problemas

### Error: "Connection refused"
```
ERROR: No se puede conectar al servidor
```
**Solución:** Asegúrese de que el servidor está ejecutándose en otra terminal antes de ejecutar el cliente.

### Error: "puerto ya está en uso"
```
Exception in thread "main" java.net.BindException: Address already in use
```
**Solución:** 
- Cierre otros programas que usen el puerto 5500
- O cambie el puerto en ambos archivos (`PUERTO = 5501`)

### Error: "Formato incorrecto"
```
ERROR: Formato incorrecto. Use: numero1;operacion;numero2
```
**Solución:** Ingrese los datos exactamente como se solicita (dos números y un operador válido).

---

## Para ejecutar en Red WiFi

Ver la sección "Pregunta 3" del archivo `ANALISIS_TEORICO.md` para instrucciones detalladas.

En resumen:
1. Obtener IP del servidor: `ipconfig` (en Windows)
2. Reemplazar `localhost` con la IP en `client.java`
3. Recompilar y ejecutar

---

## Diagrama de ejecución

```
Terminal 1 (Servidor)           Terminal 2 (Cliente)
│                                │
├─ java server                   │
│  (esperando conexión)          │
│  (BLOQUEADO en accept())       │
│                                │
│                                ├─ java client
│                                │  (intenta conectar)
│◄───── Conexión establecida ────┤
│                                │
│  (leyendo datos)               │
│  (BLOQUEADO en readLine())      │
│                                │
│                                ├─ Ingresa números y operación
│                                ├─ Envía: "15;+;30"
│◄─────── Recibe datos ──────────┤
│                                │
├─ Calcula: 15 + 30 = 45        │
├─ Envía resultado ─────────────►│
│                                │
│  Cierra conexión               │ Recibe: "45"
│  (vuelve a accept())           │ Imprime resultado
│                                │ Cierra conexión
│  (BLOQUEADO esperando nuevo    │
│   cliente)                     │ (programa termina)
│                                │
```

