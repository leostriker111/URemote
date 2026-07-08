"""Se cumple justo después de prender la compu (uptime < margen minutos)."""

import ctypes
import time

AYUDA = "margen=3 (minutos desde el arranque)"


def se_cumple(params, entrada):
    ms = ctypes.windll.kernel32.GetTickCount64()
    if ms > int(params.get("margen", 3)) * 60_000:
        return None
    # sello por arranque: época del boot en cubetas de 5 min (aguanta jitter)
    return f"arranque {int(time.time() - ms / 1000) // 300}"
