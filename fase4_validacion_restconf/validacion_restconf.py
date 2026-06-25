"""
validacion_restconf.py
EP3 - DRY7122 - Alumno 001V-18 (Salgado Flores Marcelo Benjamin)

Valida, via RESTCONF (solo lectura - GET), que la configuracion aplicada
por Ansible en la Fase 2 coincide con los valores esperados en
vars/vars_001V-18.yaml. Segunda fuente de verdad, independiente de NETCONF.
"""

import json
import socket
from datetime import datetime

import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_NAME = "validacion_restconf.py"
VARS_FILE = "../vars/vars_001V-18.yaml"
RESPONSES_DIR = "responses"

BASE_URL = "https://192.168.56.101/restconf/data"
AUTH = ("cisco", "cisco123!")
HEADERS = {"Accept": "application/yang-data+json"}

ENDPOINTS = {
    "hostname": {
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/hostname",
        "archivo": "get_hostname.json",
    },
    "loopback": {
        "url": f"{BASE_URL}/ietf-interfaces:interfaces/interface=Loopback10",
        "archivo": "get_loopback.json",
    },
    "interfaces": {
        "url": f"{BASE_URL}/ietf-interfaces:interfaces/interface=GigabitEthernet1",
        "archivo": "get_interfaces.json",
    },
    "ntp": {
        "url": f"{BASE_URL}/Cisco-IOS-XE-native:native/ntp",
        "archivo": "get_ntp.json",
    },
}


def cargar_vars():
    with open(VARS_FILE) as f:
        return yaml.safe_load(f)


def consultar(nombre, info):
    resp = requests.get(info["url"], auth=AUTH, headers=HEADERS, verify=False, timeout=20)
    resp.raise_for_status()
    datos = resp.json()
    ruta_salida = f"{RESPONSES_DIR}/{info['archivo']}"
    with open(ruta_salida, "w") as f:
        json.dump(datos, f, indent=2)
    return datos, ruta_salida


def main():
    print("=" * 70)
    print(f"Script        : {SCRIPT_NAME}")
    print(f"Fecha/Hora    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host VM       : {socket.gethostname()}")
    print("=" * 70)

    datos_vars = cargar_vars()
    alumno = datos_vars["alumno"]
    cliente = datos_vars["cliente"]
    router = datos_vars["router"]

    print(f"Alumno        : {alumno['codigo']} - {alumno['nombre']}")
    print(f"Cliente       : {cliente['empresa']}")
    print("-" * 70)

    resultados_raw = {}
    for nombre, info in ENDPOINTS.items():
        try:
            datos, ruta = consultar(nombre, info)
            resultados_raw[nombre] = datos
            print(f"[OK]   GET {info['url']}")
            print(f"       -> guardado en {ruta}")
        except Exception as e:
            resultados_raw[nombre] = None
            print(f"[FAIL] GET {info['url']}")
            print(f"       -> error: {e}")

    print("-" * 70)

    # --- Extraccion de valores de cada respuesta JSON ---

    hostname_actual = resultados_raw.get("hostname", {})
    if hostname_actual:
        hostname_actual = hostname_actual.get("Cisco-IOS-XE-native:hostname")
    else:
        hostname_actual = None

    loopback_json = resultados_raw.get("loopback") or {}
    loopback_ip = None
    try:
        iface = loopback_json["ietf-interfaces:interface"]
        ipv4 = iface.get("ietf-ip:ipv4", {})
        direcciones = ipv4.get("address", [])
        if direcciones:
            loopback_ip = direcciones[0].get("ip")
    except (KeyError, IndexError, TypeError):
        loopback_ip = None

    interfaces_json = resultados_raw.get("interfaces") or {}
    desc_wan = None
    try:
        desc_wan = interfaces_json["ietf-interfaces:interface"].get("description")
    except (KeyError, TypeError):
        desc_wan = None

    ntp_json = resultados_raw.get("ntp") or {}
    ntp_server = None
    try:
        server_list = ntp_json["Cisco-IOS-XE-native:ntp"]["Cisco-IOS-XE-ntp:server"]["server-list"]
        if server_list:
            ntp_server = server_list[0].get("ip-address")
    except (KeyError, IndexError, TypeError):
        ntp_server = None

    # --- Comparacion contra valores esperados ---
    criterios = [
        ("Hostname corporativo", hostname_actual, cliente["hostname"]),
        ("IP Loopback", loopback_ip, router["loopback_ip"]),
        ("Descripcion WAN", desc_wan, router["descripcion_wan"]),
        ("Servidor NTP", ntp_server, router["ntp_server"]),
    ]

    ok_count = 0
    for nombre_criterio, obtenido, esperado in criterios:
        es_ok = obtenido == esperado
        if es_ok:
            ok_count += 1
        etiqueta = "[OK]  " if es_ok else "[FAIL]"
        print(f"{etiqueta} {nombre_criterio:22s} | esperado: {str(esperado):20s} | obtenido: {obtenido}")

    print("-" * 70)
    total = len(criterios)
    print(f"Resultado: {ok_count}/{total} criterios [OK]")

    if ok_count == total:
        print("RESULTADO GLOBAL: CONFORME")
    else:
        print("RESULTADO GLOBAL: NO CONFORME")

    print("=" * 70)


if __name__ == "__main__":
    main()
