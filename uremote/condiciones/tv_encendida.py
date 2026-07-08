"""Se cumple cuando la tele de la entrada aparece en la red (estaba apagada)."""

import socket
from datetime import datetime

from uremote.core import devices, registry, state

AYUDA = "puerto=auto (usa el del perfil de la tv; detecta el encendido)"


def se_cumple(params, entrada):
    nombre, datos = devices.obtener(entrada.get("tv"))
    perfil = registry.cargar_perfil(datos["perfil"])
    puerto = int(params.get("puerto", 0) or perfil.get("puerto", 0))
    if not puerto:
        raise ValueError(f"el perfil {datos['perfil']} no declara puerto; "
                         "usa puerto=NNNN en la condición")
    try:
        socket.create_connection((datos["ip"], puerto), timeout=2).close()
        en_linea = True
    except OSError:
        en_linea = False
    antes = state.leer(nombre).get("campos", {}).get("_en_linea") == "si"
    state.poner_campo(nombre, "_en_linea", "si" if en_linea else "no")
    if en_linea and not antes:
        return f"{nombre} encendida {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return None
