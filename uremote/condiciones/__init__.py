"""Condiciones enchufables de la agenda: 1 archivo = 1 condición.

Cada módulo expone AYUDA (texto de parámetros) y
se_cumple(params, entrada) -> sello | None: regresa un sello (texto que
identifica ESTA ocurrencia) cuando la condición se cumple ahorita.
La agenda encadena condiciones con Y, y dispara una vez por sello.
"""

import importlib
from pathlib import Path


def cargar(tipo: str):
    try:
        return importlib.import_module(f"uremote.condiciones.{tipo}")
    except ModuleNotFoundError:
        raise ValueError(f"condición desconocida: '{tipo}' "
                         f"(hay: {', '.join(lista())})")


def lista():
    aqui = Path(__file__).parent
    return sorted(p.stem for p in aqui.glob("*.py")
                  if not p.stem.startswith("_"))
