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

*(Completar/confirmar esta tabla con los valores reales verificados en Fase 3 y 4.)*

## 6. Resultados de validación

| Criterio | NETCONF | RESTCONF |
|---|---|---|
| Hostname corporativo | _PENDIENTE_ | _PENDIENTE_ |
| IP Loopback | _PENDIENTE_ | _PENDIENTE_ |
| Descripción WAN | _PENDIENTE_ | _PENDIENTE_ |
| Servidor NTP | _PENDIENTE_ | _PENDIENTE_ |

*(Reemplazar por CONFORME / NO CONFORME según el resultado real de cada script de validación, una vez ejecutados en Fase 3 y 4.)*

## 7. Conclusiones

*(Completar en Fase 5 con el estado final real del equipo, si fue entregado a operaciones, resultado del certificado de compliance y observaciones relevantes del proceso — por ejemplo, fallas encontradas y cómo se corrigieron.)*
