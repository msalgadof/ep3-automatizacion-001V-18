# EP3 — Implementación de Automatización de Red con Compliance Auditado

**Alumno:** Salgado Flores Marcelo Benjamin
**Código:** 001V-18
**Asignatura:** DRY7122 — Programación y Redes Virtualizadas (SDN-NFV)
**Cliente:** Vigilancia Remota SA

---

## 1. Objetivo del proyecto

Este proyecto implementó la incorporación automatizada de un nuevo router corporativo (CSR1kv) a la red de Vigilancia Remota SA, aplicando la configuración estándar de la empresa mediante Ansible y verificando su correcta aplicación de forma independiente con NETCONF y RESTCONF. El objetivo final fue dejar el equipo operativo, documentado y auditable mediante un certificado de compliance respaldado por evidencia real de ejecución.

## 2. Alcance

El trabajo cubrió: respaldo de la configuración inicial del router, habilitación de los servicios de automatización (NETCONF/RESTCONF/HTTPS), aplicación de la configuración corporativa (hostname, banner, NTP, descripción de interfaz WAN e interfaz Loopback de gestión), y la verificación independiente de cada cambio mediante dos protocolos distintos. Quedó fuera del alcance cualquier configuración de enrutamiento dinámico, seguridad perimetral (ACLs/firewall) o integración con sistemas de monitoreo (NMS), ya que el objetivo del ticket era únicamente el aprovisionamiento inicial y su validación de compliance. Las herramientas utilizadas fueron pyATS/Genie, Ansible, ncclient (NETCONF) y la librería requests de Python (RESTCONF).

## 3. Infraestructura utilizada

- **Router cliente:** Cisco CSR1000v (CSR1kv), IOS-XE.
- **Estación de trabajo:** DEVASC VM (usuario `devasc`, host `labvm`).
- **Herramientas de automatización:** Ansible (módulo `ios_config`/`ios_command`), pyATS/Genie, Python 3 con `ncclient` y `requests`.
- **Control de versiones:** Repositorio Git/GitHub `ep3-automatizacion-001V-18`.

## 4. Tecnologías empleadas y justificación

- **pyATS/Genie:** se usó en la Fase 1 y Fase 5 porque se conecta vía SSH y no depende de que NETCONF/RESTCONF estén habilitados, lo que permite capturar el estado real del equipo "tal como llegó" y compararlo objetivamente contra el estado final.
- **Ansible:** se usó en la Fase 2 porque permite aplicar la configuración corporativa de forma declarativa, reproducible e idempotente, evitando errores manuales de tipeo en el router.
- **NETCONF (ncclient):** se usó en la Fase 3 porque entrega el árbol de configuración completo en XML directamente desde el modelo de datos del dispositivo, sirviendo como verificación independiente del trabajo realizado por Ansible.
- **RESTCONF (requests):** se usó en la Fase 4 porque permite consultar recursos puntuales en JSON vía HTTPS, aportando una segunda fuente de verdad independiente de NETCONF y de Ansible.

## 5. Configuración aplicada

| Parámetro | Valor final |
|---|---|
| Hostname | RTR-VIGREM |
| Banner de acceso | ACCESO RESTRINGIDO - VIGREM |
| Servidor NTP | 8.8.8.8 |
| Descripción interfaz WAN (Gi1) | Enlace-WAN-Chillan |
| Interfaz Loopback | Loopback10 |
| IP Loopback de gestión | 10.1.18.1 / 255.255.255.0 |
| NETCONF | habilitado (netconf-yang) |
| RESTCONF | habilitado (restconf) |
| HTTPS server | habilitado (ip http secure-server) |

Todos los valores fueron verificados de forma independiente vía NETCONF y RESTCONF (ver sección 6) y confirmados contra el estado inicial mediante el diff de Genie (Fase 5), que detectó el cambio de descripción en GigabitEthernet1 (de "VBox" a "Enlace-WAN-Chillan") y la creación de la interfaz Loopback10.

## 6. Resultados de validación

| Criterio | NETCONF | RESTCONF |
|---|---|---|
| Hostname corporativo | CONFORME | CONFORME |
| IP Loopback | CONFORME | CONFORME |
| Descripción WAN | CONFORME | CONFORME |
| Servidor NTP | CONFORME | CONFORME |
| Máscara Loopback | CONFORME | *(no verificado por RESTCONF, fuera del set de 4 endpoints pedidos)* |

**Resultado NETCONF: 5/5 CONFORME**
**Resultado RESTCONF: 4/4 CONFORME**
**Certificado de compliance final: CONFORME**

## 7. Conclusiones

El router RTR-VIGREM quedó correctamente aprovisionado con la configuración corporativa de Vigilancia Remota SA y fue certificado como **CONFORME**, listo para pasar a operaciones. Los tres mecanismos de verificación independientes (Ansible idempotente, NETCONF y RESTCONF) coincidieron entre sí y contra los valores esperados en `vars_001V-18.yaml`, lo que da alta confianza en que el cambio fue aplicado correctamente y de forma reproducible.

**Observaciones y lecciones aprendidas durante el proceso:**

- **Conexión SSH no interactiva (Fase 1):** un testbed de pyATS con los campos `protocol` y `port` declarados por separado generó un comando SSH mal formado (el puerto `22` se interpretó como un comando remoto en lugar de un flag `-p`), causando un error de conexión poco descriptivo (`Failed while bringing device to "any" state`). Se resolvió retirando el campo `port` explícito.
- **Idempotencia de Ansible (Fase 2):** la línea `no shutdown` en la interfaz Loopback nunca llegaba a estado `ok` en ejecuciones repetidas, porque IOS-XE no imprime ese comando en el `running-config` cuando es el valor por defecto (las Loopback nacen activas). Se retiró esa línea, ya innecesaria.
- **Namespaces YANG mixtos (Fases 3 y 4):** algunos contenedores del modelo `Cisco-IOS-XE-native` (como `ntp/server`) declaran su propio namespace distinto al namespace nativo. Tanto en NETCONF (XML) como en RESTCONF (JSON, con el prefijo `Cisco-IOS-XE-ntp:server`), hubo que ajustar la extracción de datos para tener esto en cuenta.
- **Inconsistencia del CLI `genie learn` (Fase 5):** para el snapshot final, el comando `genie learn` fallaba de forma intermitente con el mismo testbed que sí funcionaba de forma estable usando la API de Python de Genie directamente. Se optó por usar la API (`device.learn()`) en scripts propios (`snapshot_final.py`, `generar_diff.py`) en lugar del wrapper CLI, manteniendo la misma herramienta tecnológica (pyATS/Genie) tal como exige la rúbrica.

Como observación menor: el archivo `rpc_reply_raw.xml` de la Fase 3 resultó más pequeño (~3.7KB) que el umbral orientativo de 5KB, simplemente porque la configuración del equipo es deliberadamente mínima (sin rutas, VLANs ni ACLs). Se optó por no inflar artificialmente el archivo para no comprometer la integridad de la evidencia.
