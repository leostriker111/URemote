"""Agenda: comandos programados por condiciones encadenadas (Y).

config/agenda.json guarda las entradas; cada una trae una lista de
condiciones (uremote/condiciones/: hora, arranque, tv_encendida...).
`tick()` las evalúa y dispara UNA vez por sello (candado `ultimo`).
Una tarea programada de Windows (agenda instalar) llama al tick cada
minuto con pythonw.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from uremote import condiciones
from uremote.core import paths

ARCHIVO = paths.CONFIG / "agenda.json"
LOG = paths.BASE / "agenda.log"
NOMBRE_TAREA = "URemoteAgenda"
SIN_VENTANA = 0x08000000  # CREATE_NO_WINDOW


def _leer():
    if not ARCHIVO.exists():
        return []
    with open(ARCHIVO, encoding="utf-8") as f:
        entradas = json.load(f)
    for e in entradas:  # formato viejo (v0.3): hora/dias sueltos
        if "condiciones" not in e:
            e["condiciones"] = [{"tipo": "hora", "hora": e.pop("hora"),
                                 "dias": e.pop("dias", "diario")}]
    return entradas


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


def agregar(accion, conds, tv=None, modo="solo", anunciar=False, notificar=True):
    for c in conds:
        condiciones.cargar(c["tipo"])  # valida que exista
        if c["tipo"] == "hora":
            datetime.strptime(c["hora"], "%H:%M")
    entradas = _leer()
    nid = max((e["id"] for e in entradas), default=0) + 1
    entradas.append({"id": nid, "condiciones": conds, "accion": accion,
                     "tv": tv, "modo": modo, "anunciar": anunciar,
                     "notificar": notificar, "pausada": False, "ultimo": ""})
    _escribir(entradas)
    return nid


def describir(e) -> str:
    partes = []
    for c in e["condiciones"]:
        extra = " ".join(str(v) for k, v in c.items() if k != "tipo" and v)
        partes.append(extra if c["tipo"] == "hora" else f"{c['tipo']} {extra}".strip())
    return " y ".join(partes)


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


def _confirmar(entrada, timeout=60):
    """Toast con botones va / ahora no; sin respuesta en `timeout` s → cancelado."""
    from uremote.core import notifica
    return notifica.confirmar("uremote agenda",
                              f"{describir(entrada)}: {entrada['accion']} "
                              "¿Lo corro?", timeout)


def _toast(titulo, cuerpo):
    from uremote.core import notifica
    notifica.toast(titulo, cuerpo)


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
    from uremote.core import control, guion
    accion = entrada["accion"]
    if accion.startswith("guion "):
        ruta, n = accion[6:].rsplit(maxsplit=1)  # la ruta puede traer espacios
        return guion.correr(ruta.strip('"'), int(n), entrada["tv"])
    return control.frase(entrada["tv"], accion)


def _sello(e):
    """Evalúa la cadena de condiciones (Y); regresa el sello combinado o None."""
    sellos = []
    for c in e["condiciones"]:
        params = {k: v for k, v in c.items() if k != "tipo"}
        s = condiciones.cargar(c["tipo"]).se_cumple(params, e)
        if not s:
            return None
        sellos.append(s)
    return " | ".join(sellos)


def tick():
    entradas = _leer()
    for e in entradas:
        if e["pausada"]:
            continue
        try:
            sello = _sello(e)
        except Exception as err:
            _log(f"[{e['id']}] condición rota: {err}")
            continue
        if not sello or e["ultimo"] == sello:
            continue
        e["ultimo"] = sello
        _escribir(entradas)  # candado antes de ejecutar: nunca se repite
        if e["modo"] == "confirmar" and not _confirmar(e):
            _log(f"[{e['id']}] cancelada (sin confirmación): {e['accion']}")
            continue
        if e["anunciar"]:
            _anunciar(f"Agenda: {e['accion']}.")
        try:
            resultado = _ejecutar(e)
            _log(f"[{e['id']}] ok: {resultado}")
            if e["notificar"]:
                _toast("uremote agenda", f"{describir(e)} — {e['accion']}")
        except Exception as err:
            _log(f"[{e['id']}] error: {err}")
            if e["notificar"]:
                _toast("uremote agenda (error)", str(err)[:120])


def instalar():
    """Registra la tarea de Windows que corre el tick cada minuto, sin ventana."""
    from uremote.core import notifica
    notifica.registrar_protocolo()  # para los botones del toast de confirmar
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
