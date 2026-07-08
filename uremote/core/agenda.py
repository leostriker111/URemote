"""Agenda: comandos programados por hora/días.

config/agenda.json guarda las entradas; `tick()` revisa si algo toca en
este minuto y lo dispara UNA vez (candado `ultimo`). Una tarea programada
de Windows (agenda instalar) llama al tick cada minuto con pythonw.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from uremote.core import paths

ARCHIVO = paths.CONFIG / "agenda.json"
LOG = paths.BASE / "agenda.log"
NOMBRE_TAREA = "URemoteAgenda"
SIN_VENTANA = 0x08000000  # CREATE_NO_WINDOW

DIAS = {"lun": 0, "mar": 1, "mie": 2, "jue": 3, "vie": 4, "sab": 5, "dom": 6}


def _leer():
    if not ARCHIVO.exists():
        return []
    with open(ARCHIVO, encoding="utf-8") as f:
        return json.load(f)


def _escribir(entradas):
    paths.asegurar(paths.CONFIG)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(entradas, f, indent=2, ensure_ascii=False)


def _log(texto):
    paths.asegurar(paths.BASE)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')}  {texto}\n")


def lista():
    return _leer()


def agregar(hora, accion, dias="diario", tv=None, modo="solo",
            anunciar=False, notificar=True):
    datetime.strptime(hora, "%H:%M")  # valida
    entradas = _leer()
    nid = max((e["id"] for e in entradas), default=0) + 1
    entradas.append({"id": nid, "hora": hora, "dias": dias, "accion": accion,
                     "tv": tv, "modo": modo, "anunciar": anunciar,
                     "notificar": notificar, "pausada": False, "ultimo": ""})
    _escribir(entradas)
    return nid


def quitar(nid):
    _escribir([e for e in _leer() if e["id"] != int(nid)])


def pausar(nid):
    entradas = _leer()
    for e in entradas:
        if e["id"] == int(nid):
            e["pausada"] = not e["pausada"]
            estado = "pausada" if e["pausada"] else "activa"
    _escribir(entradas)
    return estado


def _dia_ok(dias, hoy):
    if dias == "diario":
        return True
    if "-" in dias:
        a, b = dias.split("-")
        return DIAS[a] <= hoy <= DIAS[b]
    return hoy in [DIAS[d.strip()] for d in dias.split(",")]


def _confirmar(entrada, timeout=60):
    """Ventanita topmost; sin respuesta en `timeout` s → cancelado."""
    import tkinter as tk
    respuesta = {"ok": False}
    raiz = tk.Tk()
    raiz.title("uremote agenda")
    raiz.attributes("-topmost", True)
    tk.Label(raiz, text=f"Son las {entrada['hora']}:\n{entrada['accion']}\n¿Lo corro?",
             font=("Segoe UI", 11), padx=20, pady=10).pack()
    marco = tk.Frame(raiz)
    marco.pack(pady=(0, 12))

    def si():
        respuesta["ok"] = True
        raiz.destroy()
    tk.Button(marco, text="va", width=10, command=si).pack(side="left", padx=6)
    tk.Button(marco, text="ahora no", width=10,
              command=raiz.destroy).pack(side="left")
    raiz.after(timeout * 1000, raiz.destroy)
    raiz.eval("tk::PlaceWindow . center")
    raiz.mainloop()
    return respuesta["ok"]


def _toast(titulo, cuerpo):
    ps = ("[Windows.UI.Notifications.ToastNotificationManager, "
          "Windows.UI.Notifications, ContentType=WindowsRuntime] > $null; "
          "$x = [Windows.UI.Notifications.ToastNotificationManager]::"
          "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
          "$t = $x.GetElementsByTagName('text'); "
          f"$t.Item(0).AppendChild($x.CreateTextNode('{titulo}')) > $null; "
          f"$t.Item(1).AppendChild($x.CreateTextNode('{cuerpo}')) > $null; "
          "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier"
          "('uremote').Show([Windows.UI.Notifications.ToastNotification]::new($x))")
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, timeout=15, creationflags=SIN_VENTANA)
    except OSError:
        pass


def _anunciar(texto):
    import tempfile
    from voz import motor
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as f:
        f.write(texto)
    try:
        motor.leer(Path(f.name))
    finally:
        Path(f.name).unlink(missing_ok=True)


def _ejecutar(entrada):
    from uremote.core import guion, intents
    accion = entrada["accion"]
    if accion.startswith("guion "):
        _, ruta, n = accion.split(maxsplit=2)
        return guion.correr(ruta, int(n), entrada["tv"])
    return intents.interpretar(accion, entrada["tv"])


def tick():
    ahora = datetime.now()
    hhmm = ahora.strftime("%H:%M")
    entradas = _leer()
    for e in entradas:
        if e["pausada"] or e["hora"] != hhmm or not _dia_ok(e["dias"], ahora.weekday()):
            continue
        sello = ahora.strftime("%Y-%m-%d ") + hhmm
        if e["ultimo"] == sello:
            continue
        e["ultimo"] = sello
        _escribir(entradas)  # candado antes de ejecutar: nunca se repite
        if e["modo"] == "confirmar" and not _confirmar(e):
            _log(f"[{e['id']}] cancelada (sin confirmación): {e['accion']}")
            continue
        if e["anunciar"]:
            _anunciar(f"Son las {e['hora']}. {e['accion']}.")
        try:
            resultado = _ejecutar(e)
            _log(f"[{e['id']}] ok: {resultado}")
            if e["notificar"]:
                _toast("uremote agenda", f"{e['hora']} — {e['accion']}")
        except Exception as err:
            _log(f"[{e['id']}] error: {err}")
            if e["notificar"]:
                _toast("uremote agenda (error)", str(err)[:120])


def instalar():
    """Registra la tarea de Windows que corre el tick cada minuto, sin ventana."""
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    exe = pythonw if pythonw.exists() else Path(sys.executable)
    if paths._PORTABLE:
        comando = f'"{exe}" "{paths.RAIZ / "agenda_tick.pyw"}"'
    else:  # instalado con pip: el paquete ya está en site-packages
        comando = f'"{exe}" -m uremote agenda tick'
    r = subprocess.run(
        ["schtasks", "/Create", "/F", "/TN", NOMBRE_TAREA,
         "/SC", "MINUTE", "/MO", "1", "/TR", comando],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"schtasks falló: {r.stderr.strip()}")
    return NOMBRE_TAREA


def desinstalar():
    subprocess.run(["schtasks", "/Delete", "/F", "/TN", NOMBRE_TAREA],
                   capture_output=True)
