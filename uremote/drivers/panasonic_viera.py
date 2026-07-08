"""Panasonic Viera (2011-2017, sin cifrado): SOAP/UPnP en puerto 55000."""

import re
import urllib.request

from uremote.drivers.base import Base

SOBRE = ('<?xml version="1.0" encoding="utf-8"?>'
         '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
         's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
         '<s:Body><u:{accion} xmlns:u="{servicio}">{args}</u:{accion}>'
         '</s:Body></s:Envelope>')

NRC = "urn:panasonic-com:service:p00NetworkControl:1"
RENDER = "urn:schemas-upnp-org:service:RenderingControl:1"


class Driver(Base):
    def _soap(self, ruta, servicio, accion, args=""):
        cuerpo = SOBRE.format(accion=accion, servicio=servicio, args=args).encode()
        req = urllib.request.Request(
            f"http://{self.ip}:55000{ruta}", data=cuerpo, method="POST",
            headers={"Content-Type": 'text/xml; charset="utf-8"',
                     "SOAPACTION": f'"{servicio}#{accion}"'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return resp.read().decode(errors="replace")

    def mandar(self, codigo):
        self._soap("/nrc/control_0", NRC, "X_SendKey",
                   f"<X_KeyEvent>{codigo}</X_KeyEvent>")

    def consultar(self):
        args = "<InstanceID>0</InstanceID><Channel>Master</Channel>"
        datos = {}
        try:
            r = self._soap("/dmr/control_0", RENDER, "GetVolume", args)
            m = re.search(r"<CurrentVolume>(\d+)</CurrentVolume>", r)
            if m:
                datos["volumen"] = int(m.group(1))
            r = self._soap("/dmr/control_0", RENDER, "GetMute", args)
            m = re.search(r"<CurrentMute>(\d+)</CurrentMute>", r)
            if m:
                datos["mute"] = bool(int(m.group(1)))
        except OSError:
            pass
        return datos
