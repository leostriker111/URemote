import argparse
from pathlib import Path

from manualhunt.hunt import buscar_pdf


def main():
    ap = argparse.ArgumentParser(prog="manualhunt",
                                 description="busca y descarga un manual PDF")
    ap.add_argument("consulta", help='ej: "panasonic viera 39as600 manual"')
    ap.add_argument("-o", "--salida", default="manuales", help="carpeta destino")
    args = ap.parse_args()
    ruta = buscar_pdf(args.consulta, Path(args.salida))
    if ruta is None:
        print("no encontré un PDF válido; afina la consulta")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
