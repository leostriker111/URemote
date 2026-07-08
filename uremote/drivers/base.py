"""Contrato mínimo de un driver. Agregar una marca = un archivo con
`class Driver(Base)` que implemente `mandar`."""


class Base:
    def __init__(self, ip: str, perfil: dict):
        self.ip = ip
        self.perfil = perfil

    def mandar(self, codigo: str):
        """Envía un código de tecla nativo de la marca."""
        raise NotImplementedError

    def escribir(self, texto: str):
        raise ValueError(f"{self.perfil['_nombre']} no soporta escribir texto")

    def consultar(self) -> dict:
        """Estado en vivo si la marca lo permite (volumen, mute, app...)."""
        return {}

    def lanzar(self, app_id: str, contenido: str = "", tipo: str = ""):
        """Abre una app (y opcionalmente un título directo) si la marca puede."""
        raise ValueError(f"{self.perfil['_nombre']} no soporta lanzar apps")
