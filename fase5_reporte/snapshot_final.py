"""
snapshot_final.py
EP3 - DRY7122 - Alumno 001V-18 (Salgado Flores Marcelo Benjamin)

Captura el snapshot final del router (post-aprovisionamiento) usando la
API de pyATS/Genie directamente (device.connect() + device.learn()),
en lugar del comando CLI 'genie learn'.

Motivo: en este entorno, el CLI 'genie learn' presenta una conexion
intermitente con el mismo testbed que ya funciona de forma 100% estable
via la API de Python (confirmado comparando ambos metodos en paralelo:
la API conecto exitosamente varias veces seguidas mientras el CLI fallaba
con el mismo testbed exacto). Se documenta como leccion aprendida en el
README. Se sigue usando la misma herramienta (pyATS/Genie), solo que
se invoca via su API en vez de su wrapper de linea de comandos.
"""

import os
from datetime import datetime
from pprint import pformat
from genie.testbed import load

TESTBED = "../fase1_baseline/testbed_001V-18.yaml"
OUTPUT_DIR = "evidencias/snapshot_final_001V-18"
FEATURES = ["interface", "platform", "routing"]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Cargando testbed: {TESTBED}")
    tb = load(TESTBED)
    dev = tb.devices["CSR1kv"]

    print("Conectando al dispositivo...")
    dev.connect(learn_hostname=True)
    print(f"Conectado. Hostname actual del equipo: {dev.name}")

    resumen = []
    for feature in FEATURES:
        print(f"Aprendiendo feature '{feature}' ...")
        ops = dev.learn(feature)
        ruta_ops = os.path.join(OUTPUT_DIR, f"{feature}_iosxe_CSR1kv_ops.txt")
        with open(ruta_ops, "w") as f:
            datos = getattr(ops, "info", None)
            if datos:
                f.write(pformat(datos, width=100))
            else:
                f.write(str(ops))
        resumen.append((feature, ruta_ops))
        print(f"  -> guardado en {ruta_ops}")

    dev.disconnect()

    ruta_resumen = os.path.join(OUTPUT_DIR, "resumen_snapshot.txt")
    with open(ruta_resumen, "w") as f:
        f.write("=== SNAPSHOT FINAL (post-aprovisionamiento) ===\n")
        f.write(f"Fecha/Hora   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dispositivo  : {dev.name}\n")
        f.write(f"Testbed      : {TESTBED}\n")
        for feature, ruta in resumen:
            f.write(f"Feature '{feature}' -> {ruta}\n")

    print("-" * 60)
    print("Snapshot final completado exitosamente.")
    print(f"Resumen guardado en: {ruta_resumen}")


if __name__ == "__main__":
    main()
