"""Driver falso para selftest y para desarrollar la GUI sin tele."""

from uremote.drivers.base import Base

ENVIADO = []  # el selftest lo inspecciona


class Driver(Base):
    def mandar(self, codigo):
        ENVIADO.append(codigo)

    def escribir(self, texto):
        ENVIADO.append(f"texto:{texto}")

    def consultar(self):
        return {"volumen": 15, "mute": False}
