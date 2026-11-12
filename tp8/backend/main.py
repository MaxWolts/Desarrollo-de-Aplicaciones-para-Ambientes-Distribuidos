"""
API REST de inventario (la del TP7) pero guardando en MongoDB.
Escrituras -> primario. Lecturas -> replicas.

Ejecutar: uvicorn main:app --host 0.0.0.0 --port 8000
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException

from db import db_escritura, db_lectura, estado_cluster


# ---------- Modelo ----------

class ProductoNuevo(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


# ---------- Arranque: indices y datos de ejemplo ----------

def preparar_base():
    for intento in range(20):
        try:
            col = db_escritura.productos
            col.create_index([("nombre_clave", ASCENDING)], unique=True)
            if col.count_documents({}) == 0:
                for n, p, s in [("Teclado", 15000.0, 10), ("Mouse", 8000.0, 25), ("Monitor 24", 180000.0, 4)]:
                    insertar(ProductoNuevo(nombre=n, precio=p, stock=s))
            print("[API] Base lista")
            return
        except PyMongoError as e:
            print(f"[API] Esperando al cluster ({type(e).__name__})...")
            time.sleep(2)


@asynccontextmanager
async def ciclo_de_vida(app):
    preparar_base()
    yield

app = FastAPI(title="API Inventario - TP8", lifespan=ciclo_de_vida)


def nuevo_id():
    """Id autoincremental (contador atomico en el primario)."""
    c = db_escritura.contadores.find_one_and_update(
        {"_id": "productos"}, {"$inc": {"valor": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
    return c["valor"]


def insertar(p: ProductoNuevo):
    doc = {"id": nuevo_id(), **p.model_dump(), "nombre_clave": p.nombre.strip().lower()}
    db_escritura.productos.insert_one(doc)
    doc.pop("_id")
    doc.pop("nombre_clave")
    return doc


SIN_CAMPOS_INTERNOS = {"_id": 0, "nombre_clave": 0}


# ---------- Endpoints ----------

@app.get("/productos")
def listar():
    print("[API] GET /productos  (LECTURA -> replica)")
    return list(db_lectura.productos.find({}, SIN_CAMPOS_INTERNOS).sort("id", ASCENDING))


@app.get("/productos/{id}")
def obtener(id: int):
    print(f"[API] GET /productos/{id}  (LECTURA -> replica)")
    p = db_lectura.productos.find_one({"id": id}, SIN_CAMPOS_INTERNOS)
    if p is None:
        raise HTTPException(404, f"Producto {id} no encontrado")
    return p


@app.post("/productos", status_code=201)
def crear(p: ProductoNuevo):
    print(f"[API] POST /productos {p.model_dump()}  (ESCRITURA -> primario)")
    try:
        return insertar(p)
    except DuplicateKeyError:
        raise HTTPException(400, f"Ya existe un producto '{p.nombre}'")


@app.get("/cluster")
def cluster():
    """Estado de los nodos del Replica Set."""
    return estado_cluster()


# ---------- Errores ----------

@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    errores = [f"{'.'.join(str(c) for c in e['loc'][1:])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(status_code=400, content={"error": "Bad Request", "detalle": errores})


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    nombres = {400: "Bad Request", 404: "Not Found"}
    return JSONResponse(status_code=exc.status_code,
                        content={"error": nombres.get(exc.status_code, "Error"), "detalle": exc.detail})


@app.exception_handler(PyMongoError)
async def error_base(request: Request, exc: PyMongoError):
    """Nodo caido, sin primario, timeout, etc. -> 503."""
    print(f"[API] ERROR DE BASE: {type(exc).__name__}: {str(exc)[:120]}")
    return JSONResponse(status_code=503, content={"error": "Service Unavailable",
                                                  "detalle": f"Base de datos no disponible ({type(exc).__name__})"})


@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    print(f"[API] ERROR 500: {exc!r}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detalle": "Error inesperado"})
