"""
API de inventario protegida con JWT y servida solo por HTTPS.
Ejecutar: python iniciar.py
"""
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from seguridad import DURACION, autenticar, crear_token, requiere_rol, usuario_actual

app = FastAPI(title="API Inventario segura - TP9")


class Credenciales(BaseModel):
    usuario: str
    clave: str


class ProductoNuevo(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


productos = {
    1: {"id": 1, "nombre": "Teclado", "precio": 15000.0, "stock": 10},
    2: {"id": 2, "nombre": "Mouse", "precio": 8000.0, "stock": 25},
    3: {"id": 3, "nombre": "Monitor 24", "precio": 180000.0, "stock": 4},
}


@app.middleware("http")
async def log_peticiones(request: Request, call_next):
    print(f"[{request.url.scheme.upper()}] {request.method} {request.url.path}")
    return await call_next(request)


# ---------- Publico ----------

@app.post("/login")
def login(c: Credenciales):
    rol = autenticar(c.usuario, c.clave)
    if rol is None:
        print(f"   [LOGIN] fallido para '{c.usuario}'")
        raise HTTPException(401, "Usuario o clave incorrectos")
    print(f"   [LOGIN] OK '{c.usuario}' rol={rol}")
    return {"access_token": crear_token(c.usuario, rol), "token_type": "Bearer",
            "expira_en_segundos": int(DURACION.total_seconds())}


# ---------- Protegido: cualquier usuario con token ----------

@app.get("/productos")
def listar(usuario: dict = Depends(usuario_actual)):
    return {"usuario": usuario["sub"], "rol": usuario["rol"], "productos": list(productos.values())}


# ---------- Protegido: solo ADMIN ----------

@app.post("/productos", status_code=201)
def crear(p: ProductoNuevo, usuario: dict = Depends(requiere_rol("ADMIN"))):
    nuevo = {"id": max(productos) + 1, **p.model_dump()}
    productos[nuevo["id"]] = nuevo
    print(f"   [OK] producto creado por {usuario['sub']}: {nuevo}")
    return nuevo


# ---------- Errores (mismo formato JSON) ----------

NOMBRES = {400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}


@app.exception_handler(StarletteHTTPException)
async def error_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, headers=getattr(exc, "headers", None),
                        content={"error": NOMBRES.get(exc.status_code, "Error"), "detalle": exc.detail})


@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    errores = [f"{'.'.join(str(c) for c in e['loc'][1:])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(status_code=400, content={"error": "Bad Request", "detalle": errores})


@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    print(f"   [ERROR 500] {exc!r}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detalle": "Error inesperado"})
