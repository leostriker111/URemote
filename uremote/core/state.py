"""Archivos de estatus por TV (estados/<tv>.json).

Recuerdan la última tecla, entrada, y campos libres del usuario
(p.ej. perfil de imagen actual) para que las macros tengan contexto.
"""

import json
from datetime import datetime

from uremote.core import paths

ENTRADAS = ("entrada", "tv", "entrada_hdmi1", "entrada_hdmi2", "entrada_hdmi3", "entrada_av")


def _ruta(tv: str):
    return paths.ESTADOS / f"{tv}.json"


def leer(tv: str) -> dict:
    ruta = _ruta(tv)
    if not ruta.exists():
        return {"tv": tv, "campos": {}}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def _escribir(tv: str, estado: dict):
    paths.asegurar(paths.ESTADOS)
    estado["actualizado"] = datetime.now().isoformat(timespec="seconds")
    with open(_ruta(tv), "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


def registrar_tecla(tv: str, tecla: str):
    estado = leer(tv)
    estado["ultima_tecla"] = tecla
    estado["teclas_enviadas"] = estado.get("teclas_enviadas", 0) + 1
    if tecla == "power":
        estado["ultimo_power"] = datetime.now().isoformat(timespec="seconds")
    if tecla in ENTRADAS:
        estado["ultima_entrada"] = tecla
    _escribir(tv, estado)


def poner_campo(tv: str, clave: str, valor: str):
    estado = leer(tv)
    estado.setdefault("campos", {})[clave] = valor
    _escribir(tv, estado)


def fusionar_vivo(tv: str, datos: dict):
    """Mezcla datos consultados en vivo al driver (volumen, mute, app...)."""
    estado = leer(tv)
    estado.update(datos)
    _escribir(tv, estado)
    return estado
