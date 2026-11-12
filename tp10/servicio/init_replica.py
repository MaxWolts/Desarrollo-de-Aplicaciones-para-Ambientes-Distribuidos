"""
Arma el Replica Set rs0 la primera vez (si ya existe, no hace nada).
Lo corre el contenedor 'init-replica' cuando los 3 nodos estan levantados.
"""
import os
import sys
import time

from pymongo import MongoClient
from pymongo.errors import OperationFailure

MIEMBROS = os.getenv("MIEMBROS", "mongo1:27017,mongo2:27017,mongo3:27017").split(",")
URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")

host, puerto = MIEMBROS[0].split(":")
nodo1 = MongoClient(host, int(puerto), directConnection=True, serverSelectionTimeoutMS=30000)

try:
    nodo1.admin.command("replSetGetStatus")
    print("[INIT] El Replica Set ya estaba configurado")
except OperationFailure as e:
    if e.code != 94:  # 94 = NotYetInitialized
        raise
    config = {
        "_id": "rs0",
        "members": [
            # el primero tiene mas prioridad: arranca como primario y lo vuelve a ser si se recupera
            {"_id": i, "host": m, "priority": 2 if i == 0 else 1}
            for i, m in enumerate(MIEMBROS)
        ],
    }
    nodo1.admin.command("replSetInitiate", config)
    print(f"[INIT] Replica Set rs0 creado con {MIEMBROS}")

# esperar a que se elija un primario
cliente = MongoClient(URI, serverSelectionTimeoutMS=2000)
for _ in range(60):
    if cliente.primary:
        print(f"[INIT] Primario elegido: {cliente.primary[0]}:{cliente.primary[1]}")
        sys.exit(0)
    time.sleep(1)
print("[INIT] No se eligio primario a tiempo")
sys.exit(1)
