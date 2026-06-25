"""
validacion_netconf.py
EP3 - DRY7122 - Alumno 001V-18 (Salgado Flores Marcelo Benjamin)

Valida, via NETCONF (solo lectura - get-config), que la configuracion
aplicada por Ansible en la Fase 2 coincide con los valores esperados
en vars/vars_001V-18.yaml. No modifica nada en el equipo.
"""

import sys
import socket
from datetime import datetime

import yaml
from lxml import etree
from ncclient import manager
from ncclient.operations.rpc import RPCError

SCRIPT_NAME = "validacion_netconf.py"
VARS_FILE = "../vars/vars_001V-18.yaml"
RPC_REPLY_PATH = "evidencias/rpc_reply_raw.xml"

NATIVE_NS = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"

# Filtro XML: pedimos el subarbol completo del modelo Cisco-IOS-XE-native
FILTER = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>
</filter>
"""


def cargar_vars():
    with open(VARS_FILE) as f:
        return yaml.safe_load(f)


def conectar():
    return manager.connect(
        host="192.168.56.101",
        port=830,
        username="cisco",
        password="cisco123!",
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        device_params={"name": "csr"},
        timeout=60,
    )


def buscar_local(xml_root, tag):
    """Busca elementos por nombre local, ignorando el namespace exacto."""
    return xml_root.xpath(f"//*[local-name()='{tag}']")


def main():
    print("=" * 70)
    print(f"Script        : {SCRIPT_NAME}")
    print(f"Fecha/Hora    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Host VM       : {socket.gethostname()}")
    print("=" * 70)

    datos = cargar_vars()
    alumno = datos["alumno"]
    cliente = datos["cliente"]
    router = datos["router"]

    print(f"Alumno        : {alumno['codigo']} - {alumno['nombre']}")
    print(f"Cliente       : {cliente['empresa']}")
    print("-" * 70)

    try:
        m = conectar()
    except Exception as e:
        print(f"[FAIL] No se pudo establecer la sesion NETCONF: {e}")
        sys.exit(1)

    try:
        respuesta = m.get_config(source="running", filter=FILTER, with_defaults="report-all-tagged")
    except RPCError as e:
        print(f"[FAIL] Error RPC NETCONF: {e}")
        m.close_session()
        sys.exit(1)
    finally:
        try:
            m.close_session()
        except Exception:
            pass

    xml_crudo = respuesta.xml
    with open(RPC_REPLY_PATH, "w") as f:
        f.write(xml_crudo)
    print(f"XML crudo de la respuesta guardado en: {RPC_REPLY_PATH}")
    print("-" * 70)

    root = etree.fromstring(xml_crudo.encode("utf-8"))

    # --- Extraccion de valores desde el arbol Cisco-IOS-XE-native ---

    # Hostname
    hostname_nodes = buscar_local(root, "hostname")
    hostname_actual = hostname_nodes[0].text.strip() if hostname_nodes else None

    # Interfaz Loopback (IP y mascara de gestion)
    loopback_ip = None
    loopback_mask = None
    for nodo in buscar_local(root, "Loopback"):
        nombre = nodo.find(f"{{{NATIVE_NS}}}name")
        if nombre is not None and nombre.text == str(router["loopback_id"]):
            primarios = nodo.xpath(".//*[local-name()='primary']")
            if primarios:
                addr = primarios[0].find(f"{{{NATIVE_NS}}}address")
                mask = primarios[0].find(f"{{{NATIVE_NS}}}mask")
                loopback_ip = addr.text if addr is not None else None
                loopback_mask = mask.text if mask is not None else None

    # Descripcion de interfaz WAN (GigabitEthernet1)
    desc_wan = None
    for nodo in buscar_local(root, "GigabitEthernet"):
        nombre = nodo.find(f"{{{NATIVE_NS}}}name")
        if nombre is not None and nombre.text == "1":
            desc = nodo.find(f"{{{NATIVE_NS}}}description")
            desc_wan = desc.text if desc is not None else None

    # Servidor NTP
    ntp_server = None
    for s in buscar_local(root, "server-list"):
        ip_nodos = s.xpath(".//*[local-name()='ip-address']")
        if ip_nodos:
            ntp_server = ip_nodos[0].text
            break

    # --- Comparacion contra valores esperados (vars_001V-18.yaml) ---
    criterios = [
        ("Hostname corporativo", hostname_actual, cliente["hostname"]),
        ("IP Loopback", loopback_ip, router["loopback_ip"]),
        ("Mascara Loopback", loopback_mask, router["loopback_mask"]),
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
