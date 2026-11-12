"""
Prueba de estres: rampa por escalones 50 -> 100 -> ... -> 300 usuarios (1 minuto cada uno).

  python -m locust -f locust/estres.py --host http://localhost:8100
"""
import os

from locust import LoadTestShape

from locustfile import UsuarioInventario  # noqa: F401  (el usuario que se simula)

ESCALONES = [50, 100, 150, 200, 250, 300]
DURACION = int(os.getenv("DURACION_ESCALON", "60"))  # segundos por escalon


class RampaPorEscalones(LoadTestShape):
    def tick(self):
        escalon = int(self.get_run_time() // DURACION)
        if escalon >= len(ESCALONES):
            return None  # fin de la prueba
        return ESCALONES[escalon], 50  # (usuarios, usuarios nuevos por segundo)
