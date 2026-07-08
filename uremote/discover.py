"""Descubrimiento de TVs en la red local vía SSDP (multicast UPnP)."""

import re
import socket
import urllib.request

MSEARCH = ("M-SEARCH * HTTP/1.1\r\n"
           "HOST: 239.255.255.250:1900\r\n"
           'MAN: "ssdp:discover"\r\n'
           "MX: 2\r\n"
           "ST: {st}\r\n\r\n")

# ST específicos primero (algunas TVs no contestan a ssdp:all)
OBJETIVOS = ("urn:panasonic-com:service:p00NetworkControl:1",
             "roku:ecp",
             "urn:dial-multiscreen-org:service:dial:1",
             "ssdp:all")


def _adivinar_perfil(respuesta: str) -> str:
    r = respuesta.lower()
    if "panasonic" in r or "p00networkcontrol" in r or "viera" in r:
        return "panasonic_viera"
    if "roku" in r:
        return "roku"
    if "samsung" in r or "tizen" in r:
        return "samsung_tizen"
    if "webos" in r or "lg electronics" in r or "lge" in r:
        return "lg_webos"
    if "dial" in r or "android" in r or "bravia" in r:
        return "androidtv"
    return "?"


def _cabecera(texto, nombre):
    return next((l.split(":", 1)[1].strip() for l in texto.splitlines()
                 if l.lower().startswith(nombre)), "")


def _datos_upnp(location):
    """Jala friendlyName/modelName del XML de descripción del dispositivo."""
    try:
        with urllib.request.urlopen(location, timeout=3) as resp:
            xml = resp.read().decode(errors="replace")
        nombre = re.search(r"<friendlyName>([^<]+)</friendlyName>", xml)
        modelo = re.search(r"<modelName>([^<]+)</modelName>", xml)
        return {"nombre": nombre.group(1).strip() if nombre else "",
                "modelo": modelo.group(1).strip() if modelo else ""}
    except OSError:
        return {"nombre": "", "modelo": ""}


def buscar(segundos=3):
    """Regresa lista de dicts {ip, perfil, server, nombre, modelo}."""
    vistos = {}
    for st in OBJETIVOS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(segundos)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        try:
            sock.sendto(MSEARCH.format(st=st).encode(), ("239.255.255.250", 1900))
            while True:
                try:
                    datos, (ip, _) = sock.recvfrom(4096)
                except socket.timeout:
                    break
                texto = datos.decode(errors="replace")
                perfil = _adivinar_perfil(texto)
                if ip not in vistos or vistos[ip]["perfil"] == "?":
                    vistos[ip] = {"ip": ip, "perfil": perfil,
                                  "server": _cabecera(texto, "server"),
                                  "location": _cabecera(texto, "location")}
        except OSError:
            pass
        finally:
            sock.close()
    for tv in vistos.values():
        tv.update(_datos_upnp(tv.pop("location")) if tv.get("location")
                  else {"nombre": "", "modelo": ""})
    return list(vistos.values())
