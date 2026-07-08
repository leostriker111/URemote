"""Rutas de datos. Corriendo desde el repo todo vive junto (portable);
instalado con pip/installer los datos van a ~/.uremote."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_PORTABLE = (RAIZ / "uremote.cmd").exists() or (RAIZ / ".git").exists()
BASE = RAIZ if _PORTABLE else Path.home() / ".uremote"

PERFILES = Path(__file__).resolve().parents[1] / "profiles"
CONFIG = BASE / "config"
MACROS = BASE / "macros"
ESTADOS = BASE / "estados"
MANUALES = BASE / "manuales"

ARCHIVO_TVS = CONFIG / "tvs.json"


def asegurar(carpeta: Path) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta
