"""
Corre las pruebas de Locust sin interfaz (headless), registrando CPU/RAM con docker stats.
Los resultados quedan en la carpeta resultados/.

  python correr_pruebas.py normal    -> carga normal: 50 usuarios, 3 min           (~3 min)
  python correr_pruebas.py estres    -> estres 50..300 usuarios, sin y con cache    (~13 min)
  python correr_pruebas.py todo      -> las dos                                     (~16 min)

Despues: python reporte.py
"""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from monitor import Monitor

RAIZ = Path(__file__).parent
RESULTADOS = RAIZ / "resultados"
API_BASE = "http://localhost:8100"   # sin cache
API_CACHE = "http://localhost:8101"  # con cache (mejora)
DURACION_NORMAL = os.getenv("DURACION_NORMAL", "180s")
PAUSA = int(os.getenv("PAUSA_ENTRE_PRUEBAS", "30"))


def chequear(url):
    try:
        with urllib.request.urlopen(url + "/salud", timeout=5) as r:
            print(f"[OK] {url} responde: {r.read().decode()}")
            return True
    except OSError as e:
        print(f"[ERROR] {url} no responde ({e}). ¿Esta levantado 'docker compose up -d --build'?")
        return False


def correr_locust(nombre, archivo, host, extra=()):
    print(f"\n=== Prueba '{nombre}' contra {host} ===")
    cmd = [sys.executable, "-m", "locust", "-f", str(RAIZ / "locust" / archivo), "--headless",
           "--host", host, "--csv", str(RESULTADOS / nombre), "--csv-full-history", "--only-summary",
           *extra]
    with Monitor(RESULTADOS / f"recursos_{nombre}.csv"):
        subprocess.run(cmd, cwd=RAIZ / "locust")  # locust devuelve codigo 1 si hubo errores: es esperable
    print(f"=== Fin '{nombre}' ===")


def normal():
    if chequear(API_BASE):
        correr_locust("normal_base", "locustfile.py", API_BASE, ["-u", "50", "-r", "10", "-t", DURACION_NORMAL])


def estres():
    if chequear(API_BASE) and chequear(API_CACHE):
        correr_locust("estres_base", "estres.py", API_BASE)
        print(f"\nPausa de {PAUSA} s para que el sistema se descargue...")
        time.sleep(PAUSA)
        correr_locust("estres_cache", "estres.py", API_CACHE)


if __name__ == "__main__":
    RESULTADOS.mkdir(exist_ok=True)
    modo = sys.argv[1] if len(sys.argv) > 1 else "todo"
    if modo in ("normal", "todo"):
        normal()
    if modo == "todo":
        print(f"\nPausa de {PAUSA} s...")
        time.sleep(PAUSA)
    if modo in ("estres", "todo"):
        estres()
    print("\nListo. Ahora: python reporte.py")
