"""Se cumple a la hora HH:MM los días indicados."""

from datetime import datetime

AYUDA = "hora=HH:MM dias=diario|lun-vie|sab,dom"

DIAS = {"lun": 0, "mar": 1, "mie": 2, "jue": 3, "vie": 4, "sab": 5, "dom": 6}


def _dia_ok(dias, hoy):
    if dias == "diario":
        return True
    if "-" in dias:
        a, b = dias.split("-")
        return DIAS[a] <= hoy <= DIAS[b]
    return hoy in [DIAS[d.strip()] for d in dias.split(",")]


def se_cumple(params, entrada):
    ahora = datetime.now()
    if (ahora.strftime("%H:%M") == params["hora"]
            and _dia_ok(params.get("dias", "diario"), ahora.weekday())):
        return ahora.strftime("%Y-%m-%d %H:%M")
    return None
