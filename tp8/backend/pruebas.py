"""
Pruebas del TP8.

  python pruebas.py estado            -> nodos del cluster y su rol
  python pruebas.py propagacion [N]   -> escribe N registros en el primario y los busca en las replicas
  python pruebas.py failover          -> escribe y lee cada 1 s; tirar el primario mientras corre
"""
import sys
import time
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.write_concern import WriteConcern

from db import URI, cliente_escritura, estado_cluster, db_escritura


def hora():
    return datetime.now().strftime("%H:%M:%S")


def nodo(par):
    return f"{par[0]}:{par[1]}" if par else "NINGUNO"


# ---------------- estado ----------------

def estado():
    print("Nodos del Replica Set rs0:")
    for m in estado_cluster():
        print(f"  {m['nodo']:<18} {m['estado']:<12} {'OK' if m['vivo'] else 'CAIDO'}")


# ---------------- propagacion ----------------

def propagacion(n):
    cliente_escritura.admin.command("ping")
    primario = cliente_escritura.primary
    secundarios = sorted(cliente_escritura.secondaries)
    print(f"Primario: {nodo(primario)} | Replicas: {[nodo(s) for s in secundarios]}\n")

    # conexion DIRECTA a cada replica (sin pasar por el primario)
    replicas = {s: MongoClient(s[0], s[1], directConnection=True, readPreference="secondaryPreferred")
                for s in secundarios}

    for w, nombre in [(1, "PEREZOSA (w=1): el primario confirma sin esperar a las replicas"),
                      (len(secundarios) + 1, f"ANSIOSA (w={len(secundarios) + 1}): el primario espera a todas las replicas")]:
        lote = f"lote-{int(time.time() * 1000)}"
        col = db_escritura.get_collection("pruebas", write_concern=WriteConcern(w=w))
        docs = [{"lote": lote, "n": i, "dato": f"registro {i}"} for i in range(n)]

        print(f"=== Replicacion {nombre} ===")
        t0 = time.perf_counter()
        col.insert_many(docs)
        t_escritura = (time.perf_counter() - t0) * 1000
        print(f"[ESCRITURA] {n} registros en el primario {nodo(primario)}: {t_escritura:.1f} ms")

        for s, c in replicas.items():
            inmediato = c["inventario"]["pruebas"].count_documents({"lote": lote})
            espera = 0.0
            while c["inventario"]["pruebas"].count_documents({"lote": lote}) < n:
                time.sleep(0.005)
                espera += 5
            print(f"[LECTURA ] replica {nodo(s)}: apenas confirmada tenia {inmediato}/{n} "
                  f"-> completa {'enseguida' if inmediato == n else f'despues de ~{espera:.0f} ms'}")
        print()


# ---------------- failover ----------------

def failover():
    # cliente propio con timeout corto para ver el fallo rapido
    cli_w = MongoClient(URI, w="majority", serverSelectionTimeoutMS=2000)
    cli_r = MongoClient(URI, readPreference="secondaryPreferred", serverSelectionTimeoutMS=2000)
    col_w = cli_w["inventario"]["failover"]
    col_r = cli_r["inventario"]["failover"]

    print("Escribiendo y leyendo cada 1 s. Tirar el primario en otra terminal (docker stop mongo1).")
    print("Ctrl+C para terminar.\n")
    ultimo_primario = None
    i = 0
    while True:
        i += 1
        try:
            col_w.insert_one({"n": i, "hora": hora()})
            primario = cli_w.primary
            if ultimo_primario and primario != ultimo_primario:
                print(f"\n*** FAILOVER: nuevo primario {nodo(primario)} (antes {nodo(ultimo_primario)}) ***\n")
            ultimo_primario = primario
            escritura = f"OK en {nodo(primario)}"
        except PyMongoError as e:
            escritura = f"FALLA ({type(e).__name__})"

        try:
            total = col_r.count_documents({})
            lectura = f"OK, {total} docs"
        except PyMongoError as e:
            lectura = f"FALLA ({type(e).__name__})"

        print(f"[{hora()}] #{i:<3} escritura: {escritura:<38} lectura: {lectura}")
        time.sleep(1)


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "estado"
    try:
        if accion == "estado":
            estado()
        elif accion == "propagacion":
            propagacion(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
        elif accion == "failover":
            failover()
        else:
            print(__doc__)
    except KeyboardInterrupt:
        print("\nFin.")
    except PyMongoError as e:
        print(f"[ERROR] No se pudo hablar con el cluster: {type(e).__name__}: {e}")
