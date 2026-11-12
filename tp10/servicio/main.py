"""
API de inventario del TP8 (FastAPI + MongoDB Replica Set), preparada para pruebas de carga.

Cambios respecto del TP8:
  - sin prints por peticion (imprimir en consola bajo carga gasta CPU y distorsiona la medicion)
  - GET /productos devuelve como maximo 50 productos (tamaño de respuesta estable)
  - CACHE_SEG > 0 activa la MEJORA: cache en memoria de las lecturas (respuesta JSON ya armada)
"""
import json
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException

from db import db_escritura, db_lectura

CACHE_SEG = float(os.getenv("CACHE_SEG", "0"))  # 0 = sin cache
LIMITE = 50
SIN_CAMPOS_INTERNOS = {"_id": 0, "nombre_clave": 0}


class ProductoNuevo(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


# ---------- cache (la mejora) ----------

_cache = {}  # clave -> (vence_en, bytes_json)


def cache_leer(clave):
    if CACHE_SEG > 0:
        item = _cache.get(clave)
        if item and item[0] > time.monotonic():
            return item[1]
    return None


def cache_guardar(clave, datos):
    if CACHE_SEG > 0:
        _cache[clave] = (time.monotonic() + CACHE_SEG, datos)


def respuesta_json(datos: bytes):
    return Response(content=datos, media_type="application/json")


# ---------- arranque ----------

def nuevo_id():
    c = db_escritura.contadores.find_one_and_update(
        {"_id": "productos"}, {"$inc": {"valor": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
    return c["valor"]


def insertar(p: ProductoNuevo):
    doc = {"id": nuevo_id(), **p.model_dump(), "nombre_clave": p.nombre.strip().lower()}
    db_escritura.productos.insert_one(doc)
    doc.pop("_id")
    doc.pop("nombre_clave")
    return doc


def preparar_base():
    for _ in range(30):
        try:
            col = db_escritura.productos
            col.create_index([("nombre_clave", ASCENDING)], unique=True)
            col.create_index([("id", ASCENDING)], unique=True)
            # productos de ejemplo con id fijo (upsert: no se duplican aunque arranquen las 2 APIs a la vez)
            for i, n, pr, s in [(1, "Teclado", 15000.0, 10), (2, "Mouse", 8000.0, 25), (3, "Monitor 24", 180000.0, 4)]:
                col.update_one({"id": i}, {"$setOnInsert": {"id": i, "nombre": n, "precio": pr, "stock": s,
                                                            "nombre_clave": n.lower()}}, upsert=True)
            db_escritura.contadores.update_one({"_id": "productos"}, {"$max": {"valor": 3}}, upsert=True)
            print(f"[API] Base lista | cache: {'ACTIVADA ' + str(CACHE_SEG) + ' s' if CACHE_SEG > 0 else 'desactivada'}")
            return
        except PyMongoError as e:
            print(f"[API] Esperando al cluster ({type(e).__name__})...")
            time.sleep(2)


@asynccontextmanager
async def ciclo_de_vida(app):
    preparar_base()
    yield

app = FastAPI(title="API Inventario - TP10", lifespan=ciclo_de_vida)


# ---------- endpoints ----------

@app.get("/salud")
def salud():
    return {"ok": True, "cache_seg": CACHE_SEG}


@app.get("/productos")
def listar():
    datos = cache_leer("lista")
    if datos is None:
        docs = list(db_lectura.productos.find({}, SIN_CAMPOS_INTERNOS).sort("id", ASCENDING).limit(LIMITE))
        datos = json.dumps(docs).encode()
        cache_guardar("lista", datos)
    return respuesta_json(datos)


@app.get("/productos/{id}")
def obtener(id: int):
    datos = cache_leer(f"producto-{id}")
    if datos is None:
        p = db_lectura.productos.find_one({"id": id}, SIN_CAMPOS_INTERNOS)
        if p is None:
            raise HTTPException(404, f"Producto {id} no encontrado")
        datos = json.dumps(p).encode()
        cache_guardar(f"producto-{id}", datos)
    return respuesta_json(datos)


@app.post("/productos", status_code=201)
def crear(p: ProductoNuevo):
    try:
        nuevo = insertar(p)
    except DuplicateKeyError:
        raise HTTPException(400, f"Ya existe un producto '{p.nombre}'")
    _cache.pop("lista", None)  # la lista cambio: se invalida la cache
    return nuevo


# ---------- errores ----------

@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Bad Request", "detalle": str(exc.errors())[:300]})


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.status_code, "detalle": exc.detail})


@app.exception_handler(PyMongoError)
async def error_base(request: Request, exc: PyMongoError):
    return JSONResponse(status_code=503, content={"error": "Service Unavailable", "detalle": type(exc).__name__})


@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    print(f"[API] ERROR 500: {exc!r}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
