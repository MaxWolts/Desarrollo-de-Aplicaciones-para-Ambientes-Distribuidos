"""
Servidor REST - Inventario de productos.
FastAPI + JSON sobre HTTP/1.1. Datos en memoria.

Ejecutar:  uvicorn main:app --port 8000
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="API Inventario - TP7")


# ---------- Modelos (el "contrato" del JSON) ----------

class ProductoNuevo(BaseModel):
    """Lo que manda el cliente en el POST."""
    nombre: str = Field(min_length=1, max_length=50)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class Producto(BaseModel):
    """Lo que devuelve el servidor (con id)."""
    id: int
    nombre: str
    precio: float
    stock: int


# ---------- "Base de datos" en memoria ----------

productos: dict[int, Producto] = {
    1: Producto(id=1, nombre="Teclado", precio=15000.0, stock=10),
    2: Producto(id=2, nombre="Mouse", precio=8000.0, stock=25),
    3: Producto(id=3, nombre="Monitor 24", precio=180000.0, stock=4),
}
siguiente_id = 4


# ---------- Endpoints ----------

@app.get("/productos", response_model=list[Producto])
def listar_productos():
    """GET: devuelve todos los productos."""
    print(f"[GET] /productos -> {len(productos)} productos")
    return list(productos.values())


@app.get("/productos/{id}", response_model=Producto)
def obtener_producto(id: int):
    """GET: devuelve un producto. 404 si no existe."""
    if id not in productos:
        print(f"[GET] /productos/{id} -> 404")
        raise HTTPException(status_code=404, detail=f"Producto {id} no encontrado")
    print(f"[GET] /productos/{id} -> {productos[id].nombre}")
    return productos[id]


@app.post("/productos", response_model=Producto, status_code=201)
async def crear_producto(nuevo: ProductoNuevo, request: Request):
    """POST: recibe un JSON, lo valida y crea el producto."""
    global siguiente_id

    cuerpo = (await request.body()).decode("utf-8")
    print(f"[POST] /productos  payload recibido: {cuerpo}")

    # regla de negocio: no repetir nombre
    if any(p.nombre.lower() == nuevo.nombre.lower() for p in productos.values()):
        raise HTTPException(status_code=400, detail=f"Ya existe un producto '{nuevo.nombre}'")

    producto = Producto(id=siguiente_id, **nuevo.model_dump())
    productos[siguiente_id] = producto
    siguiente_id += 1
    print(f"[POST] creado -> {producto.model_dump()}")
    return producto


@app.get("/error-simulado")
def error_simulado():
    """Fuerza un fallo interno para probar el 500."""
    print("[GET] /error-simulado -> se fuerza una excepcion")
    raise RuntimeError("Fallo simulado en el servidor")


# ---------- Manejo de errores ----------

@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    """JSON mal formado o datos invalidos -> 400 Bad Request."""
    errores = [f"{'.'.join(str(c) for c in e['loc'][1:])}: {e['msg']}" for e in exc.errors()]
    print(f"[ERROR 400] {request.method} {request.url.path} -> {errores}")
    return JSONResponse(status_code=400, content={"error": "Bad Request", "detalle": errores})


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    """404, 400 de negocio, etc. con el mismo formato."""
    nombres = {400: "Bad Request", 404: "Not Found"}
    print(f"[ERROR {exc.status_code}] {request.method} {request.url.path} -> {exc.detail}")
    return JSONResponse(status_code=exc.status_code,
                        content={"error": nombres.get(exc.status_code, "Error"), "detalle": exc.detail})


@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    """Cualquier otro error -> 500 Internal Server Error (sin mostrar detalles internos)."""
    print(f"[ERROR 500] {request.method} {request.url.path} -> {exc!r}")
    return JSONResponse(status_code=500,
                        content={"error": "Internal Server Error", "detalle": "Error inesperado en el servidor"})
