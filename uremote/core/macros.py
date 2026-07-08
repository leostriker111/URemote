"""Macros: archivos de texto en macros/ con un comando por línea.

Sintaxis (igual que el CLI sin el prefijo `uremote`):
    mandar vol+
    espera 0.5
    texto hola
    # comentario
"""

import time

from uremote.core import paths


def _ruta(nombre: str):
    return paths.MACROS / f"{nombre}.txt"


def lista():
    if not paths.MACROS.exists():
        return []
    return sorted(p.stem for p in paths.MACROS.glob("*.txt"))


def ver(nombre: str) -> str:
    ruta = _ruta(nombre)
    if not ruta.exists():
        raise ValueError(f"macro desconocida: {nombre}")
    return ruta.read_text(encoding="utf-8")


def anotar(nombre: str, linea: str):
    paths.asegurar(paths.MACROS)
    with open(_ruta(nombre), "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def correr(nombre: str, ejecutor, eco=None):
    """Corre la macro línea por línea. `ejecutor(partes)` manda el comando,
    `eco(texto)` reporta avance (opcional)."""
    for cruda in ver(nombre).splitlines():
        linea = cruda.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = linea.split()
        if eco:
            eco(linea)
        if partes[0] == "espera":
            time.sleep(float(partes[1]))
        else:
            ejecutor(partes)
