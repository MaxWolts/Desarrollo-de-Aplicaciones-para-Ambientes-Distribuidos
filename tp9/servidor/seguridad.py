"""
Autenticacion y autorizacion con JWT (HS256).
  - usuarios con contraseña hasheada (PBKDF2 + salt)
  - crear_token(): firma el JWT con sub, rol, iat, exp
  - usuario_actual(): valida el header Authorization: Bearer <token>  -> 401
  - requiere_rol():   controla el rol del token                        -> 403
"""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

CLAVE_SECRETA = os.getenv("JWT_SECRETO", "clave-super-secreta-del-tp9-cambiar-en-produccion")
ALGORITMO = "HS256"
DURACION = timedelta(seconds=int(os.getenv("JWT_DURACION_SEG", "120")))  # 2 minutos


# ---------- Contraseñas (nunca en texto plano) ----------

def hashear(clave: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", clave.encode(), salt, 100_000)


def _crear_usuario(clave, rol):
    salt = os.urandom(16)
    return {"salt": salt, "hash": hashear(clave, salt), "rol": rol}


USUARIOS = {
    "admin": _crear_usuario("admin123", "ADMIN"),
    "max": _crear_usuario("max123", "USER"),
}


def autenticar(usuario: str, clave: str):
    """Devuelve el rol si usuario y clave son correctos, si no None."""
    u = USUARIOS.get(usuario)
    if u and hmac.compare_digest(hashear(clave, u["salt"]), u["hash"]):
        return u["rol"]
    return None


# ---------- Tokens ----------

def crear_token(usuario: str, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {"sub": usuario, "rol": rol, "iat": ahora, "exp": ahora + DURACION}
    return jwt.encode(payload, CLAVE_SECRETA, algorithm=ALGORITMO)


def no_autorizado(motivo: str):
    print(f"   [AUTH] 401 -> {motivo}")
    return HTTPException(401, motivo, headers={"WWW-Authenticate": "Bearer"})


bearer = HTTPBearer(auto_error=False)


def usuario_actual(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    """Middleware de autenticacion: valida firma y expiracion del token."""
    if cred is None:
        raise no_autorizado("Falta el token (header Authorization: Bearer <token>)")
    try:
        # verifica firma + exp; algorithms fijo para que no acepte 'none' ni otro algoritmo
        datos = jwt.decode(cred.credentials, CLAVE_SECRETA, algorithms=[ALGORITMO],
                           options={"require": ["sub", "rol", "exp"]})
    except jwt.ExpiredSignatureError:
        raise no_autorizado("Token expirado")
    except jwt.InvalidSignatureError:
        raise no_autorizado("Firma invalida: el token fue alterado")
    except jwt.InvalidTokenError as e:
        raise no_autorizado(f"Token invalido ({type(e).__name__})")
    print(f"   [AUTH] token OK -> sub={datos['sub']} rol={datos['rol']}")
    return datos


def requiere_rol(*roles):
    """Middleware de autorizacion: el rol del token tiene que estar en la lista."""
    def verificar(datos: dict = Depends(usuario_actual)) -> dict:
        if datos["rol"] not in roles:
            print(f"   [AUTH] 403 -> rol {datos['rol']} sin permiso (requiere {roles})")
            raise HTTPException(403, f"El rol {datos['rol']} no tiene permiso para esta operacion")
        return datos
    return verificar
