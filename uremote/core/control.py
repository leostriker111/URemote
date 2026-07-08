"""Punto único de envío: resuelve tv → perfil → driver, graba macro
si toca y actualiza el estado. CLI y GUI llaman aquí."""

from uremote.core import devices, macros, registry, state


def _driver(nombre_tv):
    nombre, datos = devices.obtener(nombre_tv)
    perfil = registry.cargar_perfil(datos["perfil"])
    return nombre, perfil, registry.cargar_driver(perfil, datos["ip"])


def enviar(nombre_tv, tecla: str) -> str:
    nombre, perfil, driver = _driver(nombre_tv)
    if tecla not in perfil["teclas"]:
        raise ValueError(f"tecla '{tecla}' no existe en {perfil['_nombre']} "
                         f"(usa: uremote teclas)")
    driver.mandar(perfil["teclas"][tecla])
    grabando = devices.grabando()
    if grabando:
        macros.anotar(grabando, f"mandar {tecla}")
    state.registrar_tecla(nombre, tecla)
    return f"{nombre} <- {tecla}"


def escribir(nombre_tv, texto: str) -> str:
    nombre, perfil, driver = _driver(nombre_tv)
    driver.escribir(texto)
    grabando = devices.grabando()
    if grabando:
        macros.anotar(grabando, f"texto {texto}")
    return f"{nombre} <- texto '{texto}'"


def abrir_app(nombre_tv, app: str, contenido: str = "", tipo: str = "") -> str:
    nombre, perfil, driver = _driver(nombre_tv)
    apps = perfil.get("apps", {})
    app_id = apps.get(app.lower(), app)  # alias del perfil o id directo
    driver.lanzar(app_id, contenido, tipo)
    grabando = devices.grabando()
    if grabando:
        extra = f" {contenido} {tipo}".rstrip()
        macros.anotar(grabando, f"app {app}{extra}")
    return f"{nombre} <- app {app}" + (f" ({contenido})" if contenido else "")


def buscar_titulo(nombre_tv, titulo: str, app: str = "") -> str:
    nombre, perfil, driver = _driver(nombre_tv)
    proveedor = perfil.get("apps", {}).get(app.lower(), "") if app else ""
    driver.buscar(titulo, proveedor)
    return f"{nombre} <- buscar '{titulo}'" + (f" en {app}" if app else "")


def frase(nombre_tv, texto: str) -> str:
    """Frase en español: primero los comandos de control conocidos (intents);
    si no es un comando, viaja cruda al buscador nativo de la tele."""
    from uremote.core import intents
    try:
        return intents.interpretar(texto, nombre_tv)
    except ValueError:
        nombre, perfil, driver = _driver(nombre_tv)
        try:
            driver.frase(texto)
        except NotImplementedError:
            raise ValueError(
                f"no entiendo '{texto}' y {perfil['_nombre']} no tiene "
                "buscador propio (agregar intent en uremote/core/intents.py)")
        grabando = devices.grabando()
        if grabando:
            macros.anotar(grabando, f"frase {texto}")
        return f"{nombre} <- frase '{texto}' (la interpreta la tele)"


def consultar(nombre_tv) -> dict:
    nombre, _, driver = _driver(nombre_tv)
    return state.fusionar_vivo(nombre, driver.consultar())


def ejecutar_linea(partes, nombre_tv=None):
    """Ejecuta una línea de macro: ['mandar', 'vol+'] o ['texto', 'hola', ...]."""
    if partes[0] == "mandar":
        for tecla in partes[1:]:
            enviar(nombre_tv, tecla)
    elif partes[0] == "texto":
        escribir(nombre_tv, " ".join(partes[1:]))
    elif partes[0] == "app":
        abrir_app(nombre_tv, *partes[1:4])
    elif partes[0] == "frase":
        frase(nombre_tv, " ".join(partes[1:]))
    else:
        raise ValueError(f"comando de macro desconocido: {partes[0]}")
