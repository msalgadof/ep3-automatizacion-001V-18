"""
generar_certificado.py
EP3 - DRY7122 - Alumno 001V-18 (Salgado Flores Marcelo Benjamin)

Lee el diff de Genie (baseline vs snapshot final) y los reportes de
validacion de las Fases 3 (NETCONF) y 4 (RESTCONF), y genera el
certificado de compliance final del proyecto.
"""

import os
import yaml
from datetime import datetime

VARS_FILE = "../vars/vars_001V-18.yaml"
DIFF_FILE = "evidencias/diff_001V-18/diff_baseline_final.txt"
NETCONF_OUTPUT = "../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt"
RESTCONF_OUTPUT = "../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt"
CERTIFICADO_PATH = "evidencias/certificado_compliance_001V-18.txt"


def cargar_vars():
    with open(VARS_FILE) as f:
        return yaml.safe_load(f)


def leer_archivo(ruta):
    if not os.path.exists(ruta):
        return None
    with open(ruta) as f:
        return f.read()


def extraer_resultado_global(contenido):
    """Busca la linea 'RESULTADO GLOBAL: ...' en el output de un script
    de validacion y devuelve CONFORME, NO CONFORME, o DESCONOCIDO."""
    if contenido is None:
        return "DESCONOCIDO (archivo no encontrado)"
    for linea in contenido.splitlines():
        if "RESULTADO GLOBAL" in linea:
            if "CONFORME" in linea and "NO CONFORME" not in linea:
                return "CONFORME"
            elif "NO CONFORME" in linea:
                return "NO CONFORME"
    return "DESCONOCIDO"


def diff_tiene_cambios(contenido):
    if contenido is None:
        return False
    return "Se detectaron" in contenido and "0 lineas de cambio" not in contenido


def main():
    os.makedirs("evidencias", exist_ok=True)
    datos = cargar_vars()
    alumno = datos["alumno"]
    cliente = datos["cliente"]
    router = datos["router"]

    diff_contenido = leer_archivo(DIFF_FILE)
    netconf_contenido = leer_archivo(NETCONF_OUTPUT)
    restconf_contenido = leer_archivo(RESTCONF_OUTPUT)

    resultado_netconf = extraer_resultado_global(netconf_contenido)
    resultado_restconf = extraer_resultado_global(restconf_contenido)
    hay_cambios = diff_tiene_cambios(diff_contenido)

    resultado_compliance = (
        "CONFORME"
        if resultado_netconf == "CONFORME"
        and resultado_restconf == "CONFORME"
        and hay_cambios
        else "NO CONFORME"
    )

    lineas = []
    lineas.append("=" * 70)
    lineas.append("CERTIFICADO DE COMPLIANCE - EP3 DRY7122")
    lineas.append("=" * 70)
    lineas.append(f"Alumno        : {alumno['codigo']} - {alumno['nombre']}")
    lineas.append(f"Cliente       : {cliente['empresa']}")
    lineas.append(f"Equipo        : {cliente['hostname']}")
    lineas.append(f"Fecha emision : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append("-" * 70)
    lineas.append("RESUMEN DE VERIFICACIONES")
    lineas.append("-" * 70)
    lineas.append(f"  Cambios detectados (Genie diff) : {'SI' if hay_cambios else 'NO'}")
    lineas.append(f"  Validacion NETCONF              : {resultado_netconf}")
    lineas.append(f"  Validacion RESTCONF             : {resultado_restconf}")
    lineas.append("-" * 70)
    lineas.append("CONFIGURACION APLICADA")
    lineas.append("-" * 70)
    lineas.append(f"  Hostname            : {cliente['hostname']}")
    lineas.append(f"  Banner de acceso    : {router['banner']}")
    lineas.append(f"  Servidor NTP        : {router['ntp_server']}")
    lineas.append(f"  Descripcion WAN     : {router['descripcion_wan']}")
    lineas.append(f"  Loopback{router['loopback_id']}         : {router['loopback_ip']}/{router['loopback_mask']}")
    lineas.append(f"  NETCONF/RESTCONF    : habilitados")
    lineas.append("=" * 70)
    lineas.append(f"RESULTADO FINAL DE COMPLIANCE: {resultado_compliance}")
    lineas.append("=" * 70)

    if resultado_compliance == "CONFORME":
        lineas.append("El equipo cumple con la configuracion corporativa estandar")
        lineas.append("y queda certificado como listo para operar.")
    else:
        lineas.append("El equipo NO cumple con uno o mas criterios verificados.")
        lineas.append("Revisar las fases correspondientes antes de certificar.")

    lineas.append("=" * 70)

    salida = "\n".join(lineas)
    print(salida)

    with open(CERTIFICADO_PATH, "w") as f:
        f.write(salida + "\n")

    print(f"\nCertificado guardado en: {CERTIFICADO_PATH}")


if __name__ == "__main__":
    main()
