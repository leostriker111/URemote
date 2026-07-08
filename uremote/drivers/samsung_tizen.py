"""Samsung Tizen (2016+): websocket wss puerto 8002 con token de pairing.

Necesita websocket-client (pip install uremote[samsung]). La primera vez
la tele muestra un diálogo 'Permitir'; el token queda en config/.
"""

import base64
import json
import ssl
import urllib.request

from uremote.core import paths
from uremote.drivers.base import Base


def _websocket():
    try:
        import websocket
        return websocket
    except ImportError:
        raise RuntimeError("el driver samsung_tizen necesita websocket-client: "
                           "pip install websocket-client")


class Driver(Base):
    def _conectar(self):
        websocket = _websocket()
        ruta = paths.CONFIG / f"samsung_{self.ip}.token"
        token = f"&token={ruta.read_text().strip()}" if ruta.exists() else ""
        nombre = base64.b64encode(b"uremote").decode()
        url = (f"wss://{self.ip}:8002/api/v2/channels/samsung.remote.control"
               f"?name={nombre}{token}")
        try:
            ws = websocket.create_connection(url, timeout=8,
                                             sslopt={"cert_reqs": ssl.CERT_NONE})
        except OSError as e:
            raise RuntimeError(f"no alcanzo la Samsung en {self.ip}:8002 ({e}); "
                               "¿está prendida y en la misma red?") from e
        ws.settimeout(30)  # la primera vez hay que picarle 'Permitir' en la tele
        r = json.loads(ws.recv())
        if r.get("event") != "ms.channel.connect":
            ws.close()
            raise RuntimeError("la Samsung no aceptó el control: acepta el "
                               "diálogo 'Permitir' en la pantalla de la tele")
        nuevo = r.get("data", {}).get("token")
        if nuevo:
            paths.asegurar(paths.CONFIG)
            ruta.write_text(str(nuevo))
        ws.settimeout(8)
        return ws

    def mandar(self, codigo):
        ws = self._conectar()
        try:
            ws.send(json.dumps({"method": "ms.remote.control", "params": {
                "Cmd": "Click", "DataOfCmd": codigo, "Option": "false",
                "TypeOfRemote": "SendRemoteKey"}}))
        finally:
            ws.close()

    def lanzar(self, app_id, contenido="", tipo=""):
        # REST aparte del websocket: puerto 8001
        req = urllib.request.Request(
            f"http://{self.ip}:8001/api/v2/applications/{app_id}",
            data=b"", method="POST")
        try:
            urllib.request.urlopen(req, timeout=6).close()
        except OSError as e:
            raise RuntimeError(f"la Samsung no abrió la app {app_id} ({e})") from e
