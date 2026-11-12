"""
Usuario virtual de Locust: simula a alguien usando la API de inventario.
  60% ver un producto | 30% listar productos | 10% crear producto
Cada usuario espera entre 0.2 y 0.8 s entre peticiones.

Prueba de carga normal (50 usuarios, 3 min) con interfaz web:
  python -m locust -f locust/locustfile.py --host http://localhost:8100
  -> abrir http://localhost:8089
"""
import random
import uuid

from locust import HttpUser, between, task

TIMEOUT = 3  # segundos: si tarda mas, cuenta como error (timeout)


class UsuarioInventario(HttpUser):
    wait_time = between(0.2, 0.8)

    @task(6)
    def ver_producto(self):
        self.client.get(f"/productos/{random.randint(1, 3)}", name="/productos/[id]", timeout=TIMEOUT)

    @task(3)
    def listar(self):
        self.client.get("/productos", timeout=TIMEOUT)

    @task(1)
    def crear(self):
        producto = {
            "nombre": f"prod-{uuid.uuid4().hex[:12]}",
            "precio": round(random.uniform(100, 50000), 2),
            "stock": random.randint(0, 100),
        }
        self.client.post("/productos", json=producto, timeout=TIMEOUT)
