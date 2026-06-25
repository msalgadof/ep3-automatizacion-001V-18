"""
generar_diff.py
EP3 - DRY7122 - Alumno 001V-18 (Salgado Flores Marcelo Benjamin)

Compara el baseline (Fase 1) contra el snapshot final (Fase 5, post-
aprovisionamiento) y reporta las diferencias detectadas. Equivalente
funcional a 'genie diff', pero implementado en Python directo sobre
los ops.info ya capturados, ya que el flujo de esta Fase 5 usa la API
de Genie en vez del CLI 'genie learn' (ver nota en snapshot_final.py).
"""

import os
import ast
import json
from datetime import datetime

BASELINE_OPS = "../fase1_baseline/evidencias/baseline_001V-18/interface_iosxe_CSR1kv_ops.txt"
FINAL_OPS = "evidencias/snapshot_final_001V-18/interface_iosxe_CSR1kv_ops.txt"
OUTPUT_DIR = "evidencias/diff_001V-18"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "diff_baseline_final.txt")


def cargar_dict(ruta):
    """Carga un archivo de ops, sea formato JSON (genie learn CLI) o
    literal de Python (pformat, usado por nuestro snapshot_final.py),
    y devuelve el diccionario de interfaces (extrae 'info' si existe)."""
    with open(ruta) as f:
        contenido = f.read()

    datos = None
    try:
        datos = json.loads(contenido)
    except Exception:
        try:
            datos = ast.literal_eval(contenido)
        except Exception:
            return None

    if isinstance(datos, dict) and "info" in datos:
        return datos["info"]
    return datos


def comparar_interfaces(baseline, final):
    diferencias = []
    todas_interfaces = set(list((baseline or {}).keys()) + list((final or {}).keys()))

    for iface in sorted(todas_interfaces):
        en_baseline = baseline.get(iface) if baseline else None
        en_final = final.get(iface) if final else None

        if en_baseline is None and en_final is not None:
            diferencias.append(f"+ Interfaz NUEVA: {iface}")
            for campo in ("description", "ipv4", "enabled"):
                if campo in en_final:
                    diferencias.append(f"    + {campo}: {en_final[campo]}")
            continue

        if en_baseline is not None and en_final is None:
            diferencias.append(f"- Interfaz ELIMINADA: {iface}")
            continue

        # Interfaz presente en ambos: comparar campos relevantes
        for campo in ("description", "ipv4", "enabled", "oper_status"):
            v_antes = en_baseline.get(campo) if en_baseline else None
            v_despues = en_final.get(campo) if en_final else None
            if v_antes != v_despues:
                diferencias.append(f"~ {iface}.{campo}:")
                diferencias.append(f"    antes  : {v_antes}")
                diferencias.append(f"    despues: {v_despues}")

    return diferencias


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    baseline = cargar_dict(BASELINE_OPS)
    final = cargar_dict(FINAL_OPS)

    lineas = []
    lineas.append("=" * 70)
    lineas.append("DIFF BASELINE (Fase 1) vs SNAPSHOT FINAL (Fase 5)")
    lineas.append(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append(f"Baseline  : {BASELINE_OPS}")
    lineas.append(f"Final     : {FINAL_OPS}")
    lineas.append("=" * 70)

    if baseline is None or final is None:
        lineas.append("[FAIL] No se pudo leer uno de los dos archivos de origen.")
    else:
        diferencias = comparar_interfaces(baseline, final)
        if diferencias:
            lineas.append(f"Se detectaron {len(diferencias)} lineas de cambio:")
            lineas.append("-" * 70)
            lineas.extend(diferencias)
        else:
            lineas.append("No se detectaron diferencias (inesperado).")

    lineas.append("=" * 70)

    salida = "\n".join(lineas)
    print(salida)

    with open(OUTPUT_FILE, "w") as f:
        f.write(salida + "\n")

    print(f"\nDiff guardado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
