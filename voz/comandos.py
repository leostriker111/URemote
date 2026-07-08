"""Frases en español → tecla canónica de uremote.

Agregar una frase = agregar una línea. Al escuchar se filtran las
que no existan en el perfil de la TV activa.
"""

FRASES = {
    "enciende": "power",
    "apaga": "power",
    "silencio": "mute",
    "sube volumen": "vol+",
    "súbele": "vol+",
    "baja volumen": "vol-",
    "bájale": "vol-",
    "canal arriba": "ch+",
    "canal abajo": "ch-",
    "arriba": "arriba",
    "abajo": "abajo",
    "izquierda": "izq",
    "derecha": "der",
    "acepta": "ok",
    "okey": "ok",
    "atrás": "atras",
    "regresa": "atras",
    "inicio": "home",
    "menú": "menu",
    "entrada": "entrada",
    "información": "info",
    "guía": "guia",
    "reproduce": "play",
    "pausa": "pausa",
    "alto": "stop",
}

FRASE_SALIR = "ya estuvo"   # corta la escucha
