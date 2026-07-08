"""Roku / Roku TV: protocolo ECP (REST) en puerto 8060."""

import re
import urllib.error
import urllib.parse
import urllib.request

from uremote.drivers.base import Base


class Driver(Base):
    def _post(self, ruta):
        req = urllib.request.Request(f"http://{self.ip}:8060{ruta}",
                                     data=b"", method="POST")
        try:
            urllib.request.urlopen(req, timeout=4).close()
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise RuntimeError(
                    "la Roku rechaza el control por red (403). En la Roku: "
                    "Configuración > Sistema > Configuración avanzada > "
                    "Control por aplicaciones móviles > Acceso de red = Predeterminado") from e
            raise RuntimeError(f"la Roku contestó HTTP {e.code} en {ruta}") from e
        except OSError as e:
            raise RuntimeError(f"no alcanzo la Roku en {self.ip}:8060 ({e})") from e

    def mandar(self, codigo):
        self._post(f"/keypress/{codigo}")

    def escribir(self, texto):
        for letra in texto:
            self._post(f"/keypress/Lit_{urllib.parse.quote(letra)}")

    def buscar(self, titulo, proveedor_id=""):
        """Búsqueda ECP: encuentra el título y lanza el primer resultado."""
        params = {"keyword": titulo, "launch": "true", "match-any": "true"}
        if proveedor_id:
            params["provider-id"] = proveedor_id
        self._post("/search/browse?" + urllib.parse.urlencode(params))

    def frase(self, texto):
        # el buscador ECP es el mismo backend que usa el micrófono del control
        self.buscar(texto)

    def lanzar(self, app_id, contenido="", tipo=""):
        ruta = f"/launch/{app_id}"
        params = {}
        if contenido:
            params["contentId"] = contenido
        if tipo:
            params["mediaType"] = tipo
        if params:
            ruta += "?" + urllib.parse.urlencode(params)
        self._post(ruta)

    def consultar(self):
        try:
            with urllib.request.urlopen(
                    f"http://{self.ip}:8060/query/active-app", timeout=4) as resp:
                cuerpo = resp.read().decode(errors="replace")
            m = re.search(r"<app[^>]*>([^<]+)</app>", cuerpo)
            return {"app_activa": m.group(1)} if m else {}
        except OSError:
            return {}
