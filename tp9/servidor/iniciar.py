"""
Levanta la API SOLO por HTTPS (puerto 8443).
Si no existe el certificado, lo genera.

Ejecutar: python iniciar.py
"""
from pathlib import Path

import uvicorn

import generar_certificado

CERTS = Path(__file__).parent / "certs"
PUERTO = 8443

if __name__ == "__main__":
    if not (CERTS / "cert.pem").exists():
        generar_certificado.generar()

    print(f"[HTTPS] Servidor en https://localhost:{PUERTO}  (no hay puerto HTTP)")
    uvicorn.run("main:app", host="0.0.0.0", port=PUERTO,
                ssl_certfile=str(CERTS / "cert.pem"),
                ssl_keyfile=str(CERTS / "key.pem"))
