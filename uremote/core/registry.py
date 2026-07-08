"""Carga de perfiles (JSON por marca) y de su driver."""

import importlib
import json

from uremote.core import paths


def lista_perfiles():
    nombres = {p.stem for p in paths.PERFILES.glob("*.json")}
    if paths.PERFILES_USUARIO.exists():
        nombres |= {p.stem for p in paths.PERFILES_USUARIO.glob("*.json")}
    return sorted(nombres)


def cargar_perfil(nombre: str) -> dict:
    ruta = paths.PERFILES_USUARIO / f"{nombre}.json"
    if not ruta.exists():
        ruta = paths.PERFILES / f"{nombre}.json"
    if not ruta.exists():
        raise ValueError(f"perfil desconocido: {nombre} (hay: {', '.join(lista_perfiles())})")
    with open(ruta, encoding="utf-8") as f:
        perfil = json.load(f)
    perfil["_nombre"] = nombre
    return perfil


def cargar_driver(perfil: dict, ip: str):
    mod = importlib.import_module(f"uremote.drivers.{perfil['driver']}")
    return mod.Driver(ip, perfil)


def teclas_de(perfil: dict):
    return sorted(perfil["teclas"].keys())
