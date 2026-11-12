"""
Conexiones al Replica Set (igual que el TP8):
  escritura -> primario | lectura -> replicas
"""
import os

from pymongo import MongoClient

URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")

# maxPoolSize: conexiones maximas a la base por cliente (pymongo usa 100 por defecto)
cliente_escritura = MongoClient(URI, readPreference="primary", w="majority", serverSelectionTimeoutMS=3000)
cliente_lectura = MongoClient(URI, readPreference="secondaryPreferred", serverSelectionTimeoutMS=3000)

db_escritura = cliente_escritura["inventario"]
db_lectura = cliente_lectura["inventario"]
