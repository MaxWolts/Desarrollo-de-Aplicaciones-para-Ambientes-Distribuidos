"""
Cliente de consola para la API de inventario.
Proceso separado del servidor: se comunica solo por HTTP + JSON.

Ejecutar:  python cliente.py [url]      (por defecto http://localhost:8000)
"""
import json
import sys

import requests

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
TIMEOUT = 5  # segundos


def mostrar_json(titulo, datos):
    print(f"{titulo}:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))


def llamar(metodo, ruta, cuerpo=None):
    """Hace la peticion, muestra lo enviado y lo recibido, y maneja los errores."""
    print(f"\n>>> {metodo} {URL}{ruta}")
    if cuerpo is not None:
        mostrar_json(">>> JSON enviado", cuerpo)

    try:
        resp = requests.request(metodo, URL + ruta, json=cuerpo, timeout=TIMEOUT)  # marshalling a JSON
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar. Esta levantado el servidor?")
        return None
    except requests.exceptions.Timeout:
        print(f"[ERROR] El servidor no respondio en {TIMEOUT} s")
        return None

    print(f"<<< Status: {resp.status_code} {resp.reason}")
    try:
        datos = resp.json()  # unmarshalling: texto JSON -> dict / list de Python
    except ValueError:
        print("[ERROR] La respuesta no es JSON valido:", resp.text[:200])
        return None
    mostrar_json("<<< JSON recibido", datos)

    if resp.status_code >= 400:
        print(f"[ERROR {resp.status_code}] {datos.get('error')}: {datos.get('detalle')}")
        return None
    return datos


# ---------- Opciones ----------

def listar():
    datos = llamar("GET", "/productos")
    if datos:
        print("\nID  NOMBRE              PRECIO      STOCK")
        for p in datos:
            print(f"{p['id']:<3} {p['nombre']:<18} ${p['precio']:>10.2f} {p['stock']:>6}")


def buscar():
    id_ = input("ID del producto: ").strip()
    p = llamar("GET", f"/productos/{id_}")
    if p:
        print(f"\nEncontrado: {p['nombre']} - ${p['precio']:.2f} - stock {p['stock']}")


def crear():
    nombre = input("Nombre: ").strip()
    precio = input("Precio: ").strip()
    stock = input("Stock: ").strip()

    # se manda tal cual lo que escribio el usuario: si esta mal, que valide el servidor
    cuerpo = {"nombre": nombre, "precio": a_numero(precio), "stock": a_numero(stock)}
    p = llamar("POST", "/productos", cuerpo)
    if p:
        print(f"\nCreado con id {p['id']}")


def a_numero(texto):
    try:
        return float(texto) if "." in texto else int(texto)
    except ValueError:
        return texto  # va como texto y el servidor responde 400


def error_simulado():
    llamar("GET", "/error-simulado")


def main():
    print(f"Cliente Inventario - servidor: {URL}")
    opciones = {"1": listar, "2": buscar, "3": crear, "4": error_simulado}
    while True:
        print("\n===== MENU =====")
        print("1) Listar productos   (GET)")
        print("2) Buscar por ID      (GET)")
        print("3) Crear producto     (POST)")
        print("4) Probar error 500")
        print("0) Salir")
        op = input("Opcion: ").strip()
        if op == "0":
            break
        accion = opciones.get(op)
        if accion:
            accion()
        else:
            print("Opcion invalida")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        pass
    print("Chau!")
