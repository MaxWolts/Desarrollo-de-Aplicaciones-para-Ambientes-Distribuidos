"""
Monitor de recursos: cada ~2 s guarda en un CSV el uso de CPU y RAM de los contenedores
(lo mismo que muestra 'docker stats').

Uso suelto:  python monitor.py resultados/recursos.csv      (Ctrl+C para cortar)
"""
import csv
import subprocess
import sys
import threading
import time
from pathlib import Path

CONTENEDORES = ["tp10-api", "tp10-api-cache", "tp10-mongo1", "tp10-mongo2", "tp10-mongo3"]
FORMATO = "{{.Name}};{{.CPUPerc}};{{.MemUsage}};{{.MemPerc}}"


def a_mb(texto):
    """'123.4MiB' / '1.2GiB' / '512kB' -> MB"""
    texto = texto.strip()
    for unidad, factor in [("GiB", 1024), ("MiB", 1), ("KiB", 1 / 1024), ("GB", 1000), ("MB", 1), ("kB", 1 / 1000), ("B", 1 / 1e6)]:
        if texto.endswith(unidad):
            return float(texto[: -len(unidad)]) * factor
    return 0.0


def leer_docker_stats():
    salida = subprocess.run(["docker", "stats", "--no-stream", "--format", FORMATO, *CONTENEDORES],
                            capture_output=True, text=True, timeout=30).stdout
    filas = []
    for linea in salida.strip().splitlines():
        nombre, cpu, mem, mem_pct = linea.split(";")
        filas.append([nombre, float(cpu.rstrip("%") or 0), round(a_mb(mem.split("/")[0]), 1),
                      float(mem_pct.rstrip("%") or 0)])
    return filas


class Monitor:
    """Se usa con 'with Monitor(archivo):' mientras corre la prueba."""

    def __init__(self, archivo):
        self.archivo = Path(archivo)
        self.parar = threading.Event()
        self.hilo = threading.Thread(target=self._bucle, daemon=True)

    def _bucle(self):
        self.archivo.parent.mkdir(exist_ok=True)
        with open(self.archivo, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "contenedor", "cpu_pct", "ram_mb", "ram_pct"])
            while not self.parar.is_set():
                try:
                    ahora = time.time()
                    for fila in leer_docker_stats():
                        w.writerow([round(ahora, 1), *fila])
                    f.flush()
                except (OSError, subprocess.SubprocessError, ValueError) as e:
                    print(f"[MONITOR] no se pudo leer docker stats: {e}")
                    return
                self.parar.wait(1)

    def __enter__(self):
        self.hilo.start()
        return self

    def __exit__(self, *_):
        self.parar.set()
        self.hilo.join(timeout=40)


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "resultados/recursos.csv"
    print(f"Registrando docker stats en {destino} (Ctrl+C para terminar)")
    with Monitor(destino):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
