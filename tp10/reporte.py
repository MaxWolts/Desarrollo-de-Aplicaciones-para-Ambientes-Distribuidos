"""
Arma las tablas y el grafico a partir de los CSV de Locust y del monitor.
Genera: resultados/reporte.md y resultados/grafico.png

  python reporte.py
"""
import csv
from pathlib import Path

RESULTADOS = Path(__file__).parent / "resultados"


def leer(archivo):
    if not archivo.exists():
        return []
    with open(archivo, newline="") as f:
        return list(csv.DictReader(f))


def num(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def prom(valores):
    valores = [v for v in valores if v is not None]
    return sum(valores) / len(valores) if valores else 0.0


# ---------------- prueba normal ----------------

def resumen_normal():
    filas = leer(RESULTADOS / "normal_base_stats.csv")
    if not filas:
        return "_No hay resultados de la prueba normal (python correr_pruebas.py normal)._\n"
    recursos = leer(RESULTADOS / "recursos_normal_base.csv")
    api = [r for r in recursos if r["contenedor"] == "tp10-api"]

    out = ["| Endpoint | Peticiones | Errores | Prom (ms) | Mín (ms) | Máx (ms) | p90 (ms) | p95 (ms) | RPS |",
           "|---|---|---|---|---|---|---|---|---|"]
    for f in filas:
        nombre = "**Total**" if f["Name"] == "Aggregated" else f"{f['Type']} {f['Name']}"
        out.append(f"| {nombre} | {f['Request Count']} | {f['Failure Count']} | {num(f['Average Response Time']):.0f} | "
                   f"{num(f['Min Response Time']):.0f} | {num(f['Max Response Time']):.0f} | {f['90%']} | {f['95%']} | "
                   f"{num(f['Requests/s']):.1f} |")
    if api:
        out.append(f"\nCPU API: promedio {prom(num(r['cpu_pct']) for r in api):.0f} % / máximo "
                   f"{max(num(r['cpu_pct']) for r in api):.0f} %  —  RAM API máx {max(num(r['ram_mb']) for r in api):.0f} MB")
    return "\n".join(out) + "\n"


# ---------------- prueba de estres ----------------

def por_escalon(nombre, contenedor):
    """Agrupa el historial de Locust por cantidad de usuarios."""
    historia = [h for h in leer(RESULTADOS / f"{nombre}_stats_history.csv") if h["Name"] == "Aggregated"]
    recursos = leer(RESULTADOS / f"recursos_{nombre}.csv")
    escalones = {}
    for h in historia:
        u = int(num(h["User Count"]) or 0)
        if u > 0:
            escalones.setdefault(u, []).append(h)

    tabla = []
    for usuarios, filas in sorted(escalones.items()):
        filas = filas[2:] or filas  # descarta los primeros segundos (mientras suben los usuarios)
        ini, fin = filas[0], filas[-1]
        n_ini, n_fin = num(ini["Total Request Count"]), num(fin["Total Request Count"])
        a_ini, a_fin = num(ini["Total Average Response Time"]), num(fin["Total Average Response Time"])
        promedio = (a_fin * n_fin - a_ini * n_ini) / (n_fin - n_ini) if n_fin and n_fin > n_ini else a_fin
        rps = prom(num(f["Requests/s"]) for f in filas)
        fps = prom(num(f["Failures/s"]) for f in filas)
        t0, t1 = num(ini["Timestamp"]), num(fin["Timestamp"])
        cpu = [num(r["cpu_pct"]) for r in recursos if r["contenedor"] == contenedor and t0 - 2 <= num(r["timestamp"]) <= t1 + 2]
        ram = [num(r["ram_mb"]) for r in recursos if r["contenedor"] == contenedor and t0 - 2 <= num(r["timestamp"]) <= t1 + 2]
        tabla.append({
            "usuarios": usuarios,
            "rps": rps,
            "promedio": promedio or 0,
            "p50": prom(num(f["50%"]) for f in filas),
            "p90": prom(num(f["90%"]) for f in filas),
            "p95": prom(num(f["95%"]) for f in filas),
            "max": max((num(f["100%"]) or 0) for f in filas),
            "error_pct": 100 * fps / rps if rps else 0,
            "cpu": max(cpu) if cpu else None,
            "ram": max(ram) if ram else None,
        })
    return tabla


def tabla_md(tabla):
    out = ["| Usuarios | RPS | Prom (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | % error | CPU API máx | RAM API máx |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for t in tabla:
        cpu = f"{t['cpu']:.0f} %" if t["cpu"] is not None else "-"
        ram = f"{t['ram']:.0f} MB" if t["ram"] is not None else "-"
        out.append(f"| {t['usuarios']} | {t['rps']:.1f} | {t['promedio']:.0f} | {t['p50']:.0f} | {t['p90']:.0f} | "
                   f"{t['p95']:.0f} | {t['max']:.0f} | {t['error_pct']:.1f} % | {cpu} | {ram} |")
    return "\n".join(out) + "\n"


def aciertos_errores(nombre):
    filas = leer(RESULTADOS / f"{nombre}_stats.csv")
    total = next((f for f in filas if f["Name"] == "Aggregated"), None)
    if not total:
        return ""
    n, e = int(num(total["Request Count"])), int(num(total["Failure Count"]))
    fallas = leer(RESULTADOS / f"{nombre}_failures.csv")
    out = [f"Total: **{n}** peticiones — **{n - e}** OK ({100 * (n - e) / n:.1f} %) — **{e}** con error ({100 * e / n:.1f} %)\n"]
    if fallas:
        out += ["| Método | Endpoint | Error | Cantidad |", "|---|---|---|---|"]
        for f in fallas:
            out.append(f"| {f['Method']} | {f['Name']} | {f['Error'][:90]} | {f['Occurrences']} |")
    return "\n".join(out) + "\n"


def grafico(base, cache):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[AVISO] matplotlib no esta instalado: no se genera el grafico (python -m pip install matplotlib)")
        return False

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
    a3 = a2.twinx()  # eje derecho para el % de error
    for tabla, etiqueta, color in [(base, "Sin cache", "#c0392b"), (cache, "Con cache", "#2471a3")]:
        if not tabla:
            continue
        u = [t["usuarios"] for t in tabla]
        a1.plot(u, [t["p95"] for t in tabla], "o-", color=color, label=f"{etiqueta} p95")
        a1.plot(u, [t["promedio"] for t in tabla], "s--", color=color, alpha=0.6, label=f"{etiqueta} promedio")
        a2.plot(u, [t["rps"] for t in tabla], "o-", color=color, label=f"{etiqueta} RPS")
        a3.bar([x + (-6 if etiqueta == "Sin cache" else 6) for x in u], [t["error_pct"] for t in tabla],
               width=12, color=color, alpha=0.3, label=f"{etiqueta} % error")
    a1.set(title="Tiempo de respuesta vs usuarios", xlabel="Usuarios concurrentes", ylabel="ms")
    a2.set(title="Throughput y errores vs usuarios", xlabel="Usuarios concurrentes", ylabel="Peticiones por segundo (RPS)")
    a3.set_ylabel("% de error")
    a3.set_ylim(0, max(10, *(t["error_pct"] * 1.2 for t in base + cache)))
    a1.grid(alpha=0.3)
    a2.grid(alpha=0.3)
    a1.legend(fontsize=8)
    h2, l2 = a2.get_legend_handles_labels()
    h3, l3 = a3.get_legend_handles_labels()
    a2.legend(h2 + h3, l2 + l3, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(RESULTADOS / "grafico.png", dpi=120)
    return True


if __name__ == "__main__":
    base = por_escalon("estres_base", "tp10-api")
    cache = por_escalon("estres_cache", "tp10-api-cache")
    hay_grafico = grafico(base, cache)

    partes = ["# Resultados\n", "## Carga normal (50 usuarios)\n", resumen_normal()]
    if base:
        partes += ["## Estrés — sin cache (original)\n", tabla_md(base),
                   "### Aciertos y errores — sin cache\n", aciertos_errores("estres_base")]
    if cache:
        partes += ["## Estrés — con cache (mejora)\n", tabla_md(cache),
                   "### Aciertos y errores — con cache\n", aciertos_errores("estres_cache")]
    if hay_grafico:
        partes.append("\n![Grafico](grafico.png)\n")

    (RESULTADOS / "reporte.md").write_text("\n".join(partes), encoding="utf-8")
    print("\n".join(partes))
    print(f"\n[OK] Generado {RESULTADOS / 'reporte.md'}" + (" y grafico.png" if hay_grafico else ""))
