"""Notificaciones de Windows: toast simple y toast con botones (confirmar).

Los botones responden por el protocolo uremote:// registrado en HKCU:
el click lanza el handler, que escribe la respuesta en
BASE/confirmaciones/<token>; `confirmar` la espera hasta el timeout.
"""

import subprocess
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape

from uremote.core import paths

SIN_VENTANA = 0x08000000  # CREATE_NO_WINDOW
CARPETA = paths.BASE / "confirmaciones"


def _pythonw():
    w = Path(sys.executable).with_name("pythonw.exe")
    return w if w.exists() else Path(sys.executable)


def _mostrar(xml):
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, "
        "Windows.UI.Notifications, ContentType=WindowsRuntime] > $null; "
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, "
        "ContentType=WindowsRuntime] > $null; "
        "$x = New-Object Windows.Data.Xml.Dom.XmlDocument; "
        "$x.LoadXml('" + xml.replace("'", "''") + "'); "
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier"
        "('uremote').Show([Windows.UI.Notifications.ToastNotification]::new($x))")
    subprocess.run(["powershell", "-NoProfile", "-Command", script],
                   capture_output=True, timeout=15, creationflags=SIN_VENTANA)


def toast(titulo, cuerpo):
    xml = ('<toast><visual><binding template="ToastGeneric">'
           f"<text>{escape(titulo)}</text><text>{escape(cuerpo)}</text>"
           "</binding></visual></toast>")
    try:
        _mostrar(xml)
    except OSError:
        pass


def confirmar(titulo, cuerpo, timeout=60):
    """Toast con botones va / ahora no. True solo si pican 'va';
    sin respuesta en `timeout` segundos se cancela."""
    registrar_protocolo()
    paths.asegurar(CARPETA)
    token = str(int(time.time()))
    archivo = CARPETA / token
    xml = ('<toast scenario="reminder" activationType="protocol" '
           f'launch="uremote://no/{token}">'
           '<visual><binding template="ToastGeneric">'
           f"<text>{escape(titulo)}</text><text>{escape(cuerpo)}</text>"
           "</binding></visual><actions>"
           f'<action content="va" arguments="uremote://ok/{token}" '
           'activationType="protocol"/>'
           f'<action content="ahora no" arguments="uremote://no/{token}" '
           'activationType="protocol"/>'
           "</actions></toast>")
    _mostrar(xml)
    for _ in range(timeout):
        if archivo.exists():
            ok = archivo.read_text(encoding="utf-8").strip() == "ok"
            archivo.unlink(missing_ok=True)
            return ok
        time.sleep(1)
    return False


def responder(url):
    """Escribe la respuesta de un click de toast: uremote://ok/<token>."""
    partes = url.replace("uremote://", "").strip("/").split("/")
    if len(partes) == 2 and partes[0] in ("ok", "no"):
        paths.asegurar(CARPETA)
        (CARPETA / partes[1]).write_text(partes[0], encoding="utf-8")


def registrar_protocolo():
    """Registra uremote:// en HKCU (idempotente)."""
    import winreg
    if paths._PORTABLE:
        comando = f'"{_pythonw()}" "{paths.RAIZ / "confirma.pyw"}" "%1"'
    else:
        comando = f'"{_pythonw()}" -m uremote confirmar "%1"'
    raiz = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\uremote")
    winreg.SetValueEx(raiz, None, 0, winreg.REG_SZ, "URL:uremote")
    winreg.SetValueEx(raiz, "URL Protocol", 0, winreg.REG_SZ, "")
    llave = winreg.CreateKey(raiz, r"shell\open\command")
    winreg.SetValueEx(llave, None, 0, winreg.REG_SZ, comando)
