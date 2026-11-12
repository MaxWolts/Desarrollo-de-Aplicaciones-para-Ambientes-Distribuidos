"""
Capa de acceso a datos.
Dos conexiones al Replica Set con el driver nativo (pymongo):
  - escritura -> siempre al PRIMARIO
  - lectura   -> a los SECUNDARIOS (replicas)
"""
import os

from pymongo import MongoClient, ReadPreference, monitoring

URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
TIMEOUT_MS = 3000  # tiempo maximo para encontrar un nodo disponible


class LogNodo(monitoring.CommandListener):
    """Muestra en consola a que nodo fue cada operacion."""
    OPERACIONES = {"find", "insert", "update", "delete", "count", "aggregate", "findAndModify"}

    def started(self, event):
        if event.command_name in self.OPERACIONES:
            host, puerto = event.connection_id
            print(f"   [{event.command_name.upper():<13}] -> nodo {host}:{puerto}")

    def succeeded(self, event):
        pass

    def failed(self, event):
        pass


log = [LogNodo()]

# Escrituras: readPreference=primary. w=majority: confirma cuando la mayoria de nodos tiene el dato
cliente_escritura = MongoClient(URI, readPreference="primary", w="majority",
                                serverSelectionTimeoutMS=TIMEOUT_MS, event_listeners=log)

# Lecturas: secondaryPreferred -> va a una replica; si no hay ninguna, usa el primario
cliente_lectura = MongoClient(URI, readPreference="secondaryPreferred",
                              serverSelectionTimeoutMS=TIMEOUT_MS, event_listeners=log)

db_escritura = cliente_escritura["inventario"]
db_lectura = cliente_lectura["inventario"]


def estado_cluster():
    """Devuelve los nodos del Replica Set y su estado (PRIMARY / SECONDARY / caido)."""
    estado = cliente_lectura.admin.command(
        "replSetGetStatus", read_preference=ReadPreference.SECONDARY_PREFERRED)
    return [{"nodo": m["name"], "estado": m["stateStr"], "vivo": m["health"] == 1}
            for m in estado["members"]]
