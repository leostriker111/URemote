"""LG webOS (2014+): websocket puerto 3000 con pairing (client-key).

Necesita websocket-client (pip install uremote[lg]). La primera vez la
tele pide aceptar el pairing en pantalla; la llave queda en config/.
Teclas del perfil: 'ssap:...' son peticiones; lo demás son botones que
van por el socket de entrada (networkinput).
"""

import json

from uremote.core import paths
from uremote.drivers.base import Base

PERMISOS = ["LAUNCH", "LAUNCH_WEBAPP", "CONTROL_AUDIO", "CONTROL_POWER",
            "CONTROL_INPUT_JOYSTICK", "CONTROL_INPUT_MEDIA_PLAYBACK",
            "CONTROL_INPUT_TV", "CONTROL_INPUT_TEXT", "READ_INSTALLED_APPS",
            "READ_CURRENT_CHANNEL", "READ_RUNNING_APPS",
            "READ_TV_CHANNEL_LIST", "WRITE_NOTIFICATION_TOAST"]


def _websocket():
    try:
        import websocket
        return websocket
    except ImportError:
        raise RuntimeError("el driver lg_webos necesita websocket-client: "
                           "pip install websocket-client")


class Driver(Base):
    def _conectar(self):
        websocket = _websocket()
        try:
            ws = websocket.create_connection(f"ws://{self.ip}:3000", timeout=8)
        except OSError as e:
            raise RuntimeError(f"no alcanzo la LG en {self.ip}:3000 ({e}); "
                               "¿está prendida y en la misma red?") from e
        ruta = paths.CONFIG / f"lg_{self.ip}.key"
        registro = {"type": "register", "payload": {
            "pairingType": "PROMPT", "manifest": {"permissions": PERMISOS}}}
        if ruta.exists():
            registro["payload"]["client-key"] = ruta.read_text().strip()
        ws.send(json.dumps(registro))
        ws.settimeout(30)  # la primera vez hay que aceptar en la pantalla
        r = json.loads(ws.recv())
        if r.get("type") == "response":  # salió el diálogo; esperar la respuesta
            r = json.loads(ws.recv())
        if r.get("type") != "registered":
            ws.close()
            raise RuntimeError("la LG no aceptó el pairing: acepta el diálogo "
                               "en la pantalla de la tele")
        llave = r["payload"].get("client-key")
        if llave:
            paths.asegurar(paths.CONFIG)
            ruta.write_text(llave)
        ws.settimeout(8)
        return ws

    def _pedir(self, ws, uri, payload=None):
        ws.send(json.dumps({"id": "u1", "type": "request",
                            "uri": f"ssap://{uri}", "payload": payload or {}}))
        return json.loads(ws.recv())

    def mandar(self, codigo):
        ws = self._conectar()
        try:
            if codigo.startswith("ssap:"):
                self._pedir(ws, codigo[5:])
            else:  # botón por el socket de entrada
                r = self._pedir(ws, "com.webos.service.networkinput/"
                                    "getPointerInputSocket")
                import websocket
                sock = websocket.create_connection(
                    r["payload"]["socketPath"], timeout=8)
                sock.send(f"type:button\nname:{codigo}\n\n")
                sock.close()
        finally:
            ws.close()

    def escribir(self, texto):
        ws = self._conectar()
        try:
            self._pedir(ws, "com.webos.service.ime/insertText",
                        {"text": texto, "replace": 0})
        finally:
            ws.close()

    def lanzar(self, app_id, contenido="", tipo=""):
        ws = self._conectar()
        try:
            payload = {"id": app_id}
            if contenido:
                payload["contentId"] = contenido
            r = self._pedir(ws, "system.launcher/launch", payload)
            if not r.get("payload", {}).get("returnValue"):
                raise RuntimeError(f"la LG no abrió {app_id}: {r}")
        finally:
            ws.close()
