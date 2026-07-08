"""TVs configuradas (config/tvs.json) y estado de grabación de macro."""

import json

from uremote.core import paths


def _leer() -> dict:
    if not paths.ARCHIVO_TVS.exists():
        return {"tvs": {}, "por_defecto": None, "grabando": None}
    with open(paths.ARCHIVO_TVS, encoding="utf-8") as f:
        return json.load(f)


def _escribir(datos: dict):
    paths.asegurar(paths.CONFIG)
    with open(paths.ARCHIVO_TVS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def lista() -> dict:
    return _leer()["tvs"]


def agregar(nombre: str, ip: str, perfil: str):
    datos = _leer()
    datos["tvs"][nombre] = {"ip": ip, "perfil": perfil}
    if datos["por_defecto"] is None:
        datos["por_defecto"] = nombre
    _escribir(datos)


def quitar(nombre: str):
    datos = _leer()
    datos["tvs"].pop(nombre, None)
    if datos["por_defecto"] == nombre:
        datos["por_defecto"] = next(iter(datos["tvs"]), None)
    _escribir(datos)


def por_defecto(nombre: str = None) -> str:
    datos = _leer()
    if nombre is not None:
        if nombre not in datos["tvs"]:
            raise ValueError(f"tv desconocida: {nombre}")
        datos["por_defecto"] = nombre
        _escribir(datos)
    return datos["por_defecto"]


def obtener(nombre: str = None) -> tuple:
    """Regresa (nombre, {ip, perfil}). Sin nombre usa la por defecto."""
    datos = _leer()
    nombre = nombre or datos["por_defecto"]
    if not nombre or nombre not in datos["tvs"]:
        raise ValueError("no hay tv configurada; usa: uremote tvs agregar <nombre> <ip> <perfil>")
    return nombre, datos["tvs"][nombre]


def grabando(macro: str = "") -> str:
    """Sin args consulta; con nombre inicia; con None detiene."""
    datos = _leer()
    if macro != "":
        datos["grabando"] = macro
        _escribir(datos)
    return datos["grabando"]
