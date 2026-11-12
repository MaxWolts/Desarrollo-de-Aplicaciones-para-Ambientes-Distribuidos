"""
Cliente de consola para probar la API segura.
Se conecta por HTTPS y VERIFICA el certificado del servidor (no usa verify=False).

Ejecutar: python cliente.py
"""
import base64
import json
import time
from pathlib import Path

import requests

URL = "https://localhost:8443"
CERT = Path(__file__).parent.parent / "servidor" / "certs" / "cert.pem"  # certificado en el que confiamos
TIMEOUT = 5

token = None  # ultimo token recibido


def mostrar(titulo, datos):
    print(f"{titulo}:\n{json.dumps(datos, indent=2, ensure_ascii=False)}")


def peticion(metodo, ruta, cuerpo=None, token_usado=None, url=None):
    url = (url or URL) + ruta
    headers = {"Authorization": f"Bearer {token_usado}"} if token_usado else {}
    print(f"\n>>> {metodo} {url}")
    if token_usado:
        print(f">>> Authorization: Bearer {token_usado[:25]}...{token_usado[-10:]}")
    if cuerpo:
        mostrar(">>> JSON enviado", cuerpo)
    try:
        r = requests.request(metodo, url, json=cuerpo, headers=headers, timeout=TIMEOUT, verify=str(CERT))
    except requests.exceptions.SSLError as e:
        print(f"[ERROR TLS] No se pudo verificar el certificado del servidor: {e.__class__.__name__}")
        return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] Conexion rechazada/cortada por el servidor")
        return None
    except requests.exceptions.Timeout:
        print(f"[ERROR] El servidor no respondio en {TIMEOUT} s")
        return None

    print(f"<<< Status: {r.status_code} {r.reason}")
    try:
        datos = r.json()
        mostrar("<<< JSON recibido", datos)
        return datos if r.ok else None
    except ValueError:
        print("<<<", r.text[:200])
        return None


# ---------- utilidades JWT (solo para mostrar / alterar, el cliente NO puede firmar) ----------

def b64_decodificar(parte):
    return json.loads(base64.urlsafe_b64decode(parte + "=" * (-len(parte) % 4)))


def b64_codificar(datos):
    return base64.urlsafe_b64encode(json.dumps(datos, separators=(",", ":")).encode()).rstrip(b"=").decode()


def ver_token(t):
    header, payload, firma = t.split(".")
    print("\nToken = header.payload.firma")
    mostrar("  header ", b64_decodificar(header))
    mostrar("  payload", b64_decodificar(payload))
    print(f"  firma  : {firma}")


def necesita_token():
    if not token:
        print("Primero hacer login (opcion 1)")
    return token is not None


# ---------- opciones ----------

def login():
    global token
    usuario = input("Usuario (admin / max): ").strip()
    clave = input("Clave (admin123 / max123): ").strip()
    datos = peticion("POST", "/login", {"usuario": usuario, "clave": clave})
    if datos:
        token = datos["access_token"]
        ver_token(token)


def listar():
    if necesita_token():
        peticion("GET", "/productos", token_usado=token)


def crear():
    if necesita_token():
        nombre = input("Nombre: ").strip()
        precio = float(input("Precio: ") or 0)
        stock = int(input("Stock: ") or 0)
        peticion("POST", "/productos", {"nombre": nombre, "precio": precio, "stock": stock}, token_usado=token)


def sin_token():
    print("\n--- Sin header Authorization ---")
    peticion("GET", "/productos")
    print("\n--- Con un token inventado ---")
    peticion("GET", "/productos", token_usado="esto.no.esunjwt")


def tampering():
    """Cambia el payload (rol -> ADMIN) y deja la firma original: el servidor debe rechazarlo."""
    if not necesita_token():
        return
    header, payload, firma = token.split(".")
    datos = b64_decodificar(payload)
    print(f"\nPayload original : {datos}")
    datos["rol"] = "ADMIN"
    datos["sub"] = "hacker"
    print(f"Payload alterado : {datos}   (sin volver a firmar)")
    alterado = f"{header}.{b64_codificar(datos)}.{firma}"
    peticion("POST", "/productos", {"nombre": "Robado", "precio": 1, "stock": 1}, token_usado=alterado)


def token_vencido():
    if not necesita_token():
        return
    exp = b64_decodificar(token.split(".")[1])["exp"]
    restante = int(exp - time.time())
    if restante > 0:
        print(f"El token vence en {restante} s. Esperando... (Ctrl+C para cancelar)")
        try:
            for s in range(restante + 1, 0, -1):
                print(f"\r  {s:>3} s ", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nCancelado")
            return
        print()
    peticion("GET", "/productos", token_usado=token)


def http_plano():
    """Intenta hablar HTTP sin cifrar con el puerto HTTPS: el servidor no lo acepta."""
    peticion("GET", "/productos", url=URL.replace("https://", "http://"))


def main():
    print(f"Cliente API segura - {URL}\nConfiando en el certificado: {CERT}")
    if not CERT.exists():
        print("[AVISO] No existe el certificado. Levantar primero el servidor (genera certs/cert.pem).")
    opciones = {"1": login, "2": listar, "3": crear, "4": sin_token,
                "5": tampering, "6": token_vencido, "7": http_plano}
    while True:
        print("\n========= MENU =========")
        print("1) Login (obtener JWT)")
        print("2) Ver productos      (GET, requiere token)")
        print("3) Crear producto     (POST, solo ADMIN)")
        print("4) Probar SIN token / token invalido")
        print("5) Probar TAMPERING (token alterado)")
        print("6) Probar token VENCIDO (espera a que expire)")
        print("7) Probar HTTP sin cifrar")
        print("0) Salir")
        op = input("Opcion: ").strip()
        if op == "0":
            break
        accion = opciones.get(op)
        accion() if accion else print("Opcion invalida")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        pass
    print("Chau!")
