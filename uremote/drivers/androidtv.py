"""Android TV / Google TV: adb por TCP (puerto 5555).

Requiere depuración por red activada en la tele y `adb` disponible
(PATH o el SDK en ~/Android/sdk/platform-tools).
"""

import shutil
import subprocess
from pathlib import Path

from uremote.drivers.base import Base


def _adb():
    exe = shutil.which("adb")
    if exe:
        return exe
    sdk = Path.home() / "Android" / "sdk" / "platform-tools" / "adb.exe"
    if sdk.exists():
        return str(sdk)
    raise RuntimeError("no encuentro adb (instala platform-tools o agrégalo al PATH)")


class Driver(Base):
    def _correr(self, *args):
        adb = _adb()
        destino = f"{self.ip}:5555"
        c = subprocess.run([adb, "connect", destino], capture_output=True,
                           text=True, timeout=6)
        salida_c = (c.stdout + c.stderr).lower()
        if "refused" in salida_c or "cannot connect" in salida_c:
            raise RuntimeError(
                f"la tele rechaza adb en {destino}. En la tele: Configuración > "
                "Preferencias del dispositivo > Acerca de > picar 7 veces "
                "'Compilación' para ser desarrollador, y luego activar "
                "Opciones para desarrolladores > Depuración por red")
        r = subprocess.run([adb, "-s", destino, *args],
                           capture_output=True, text=True, timeout=8)
        salida = (r.stdout + r.stderr).lower()
        if "unauthorized" in salida:
            raise RuntimeError("la tele pide autorización: acepta el diálogo "
                               "'¿Permitir depuración?' en la pantalla de la tele")
        if r.returncode != 0:
            raise RuntimeError(f"adb falló: {r.stderr.strip() or r.stdout.strip()}")
        return r.stdout

    def mandar(self, codigo):
        self._correr("shell", "input", "keyevent", codigo)

    def escribir(self, texto):
        self._correr("shell", "input", "text", texto.replace(" ", "%s"))

    def consultar(self):
        try:
            salida = self._correr("shell", "dumpsys", "window", "displays")
            for linea in salida.splitlines():
                if "mCurrentFocus" in linea:
                    return {"app_activa": linea.split()[-1].rstrip("}")}
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            pass
        return {}
