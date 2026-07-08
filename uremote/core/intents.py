"""Frase en español → acción sobre la tele. Tabla de regex extendible:
agregar un intent = una tupla (patrón con grupos nombrados, función)."""

import re

from uremote.core import control


def _power(m, tv):
    return control.enviar(tv, "power")


def _mute(m, tv):
    return control.enviar(tv, "mute")


def _volumen(m, tv):
    tecla = "vol+" if m.group("dir").startswith("su") or "úb" in m.group("dir") else "vol-"
    veces = int(m.group("n") or 1)
    for _ in range(veces):
        r = control.enviar(tv, tecla)
    return f"{r} x{veces}" if veces > 1 else r


def _canal(m, tv):
    for digito in m.group("n"):
        r = control.enviar(tv, digito)
    return r


def _reproducir(m, tv):
    return control.buscar_titulo(tv, m.group("titulo").strip(), m.group("app"))


def _abrir_app(m, tv):
    return control.abrir_app(tv, m.group("app"))


INTENTS = (
    (r"^(?:apaga|prende|enciende)(?: la| el)?(?: tele| tv|le)?$", _power),
    (r"^(?:silencio|mute|cállate)$", _mute),
    (r"^(?P<dir>sube|súbele|subele|baja|bájale|bajale)(?: el| al)?(?: volumen)"
     r"(?: (?P<n>\d+))?$", _volumen),
    (r"^pon(?: el)? canal (?P<n>\d+)$", _canal),
    (r"^(?:reproduce|pon) en (?P<app>\w+) (?P<titulo>.+)$", _reproducir),
    (r"^abre (?P<app>\w+)$", _abrir_app),
)


def interpretar(frase: str, tv=None) -> str:
    """Ejecuta la frase. Primero intents con argumento, luego las frases
    exactas del vocabulario de voz."""
    frase = frase.strip().lower().rstrip(".")
    for patron, accion in INTENTS:
        m = re.match(patron, frase)
        if m:
            return accion(m, tv)
    from voz.comandos import FRASES
    if frase in FRASES:
        return control.enviar(tv, FRASES[frase])
    raise ValueError(f"no entiendo: '{frase}' (agregar en uremote/core/intents.py)")
