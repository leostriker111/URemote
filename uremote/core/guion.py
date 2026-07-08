"""Guiones: txt con comandos de voz numerados.

    // nota que describe el comando de abajo
    1"reproduce en netflix love death and robots";
    2"apaga la tele";
"""

import re

from uremote.core import control

_ENTRADA = re.compile(r'^\s*(\d+)\s*"(.+?)"\s*;?\s*$')


def cargar(ruta) -> dict:
    """Regresa {numero: {"frase":..., "nota":...}}."""
    entradas, notas = {}, []
    for linea in open(ruta, encoding="utf-8").read().splitlines():
        linea = linea.strip()
        if linea.startswith("//"):
            notas.append(linea[2:].strip())
            continue
        m = _ENTRADA.match(linea)
        if m:
            entradas[int(m.group(1))] = {"frase": m.group(2),
                                         "nota": " ".join(notas)}
            notas = []
    if not entradas:
        raise ValueError(f"sin comandos numerados en {ruta}")
    return entradas


def correr(ruta, numero: int, tv=None) -> str:
    entradas = cargar(ruta)
    if numero not in entradas:
        raise ValueError(f"no hay comando {numero} (hay: {sorted(entradas)})")
    return control.frase(tv, entradas[numero]["frase"])
