import argparse
import sys
from pathlib import Path

from voz import comandos, motor


def cmd_voces(args):
    for v in motor.voces():
        print(f"  {v}")


def cmd_leer(args):
    ruta = Path(args.archivo)
    if not ruta.exists():
        sys.exit(f"no existe: {ruta}")
    wav = args.wav
    if wav == "AUTO":                      # --wav sin ruta: junto al txt
        wav = str(ruta.with_suffix(".wav"))
    if wav:
        modo = "y reproduciendo" if args.oir else "en silencio"
        print(f"generando {wav} {modo}...")
    motor.leer(ruta, voz=args.voz, wav=wav, velocidad=args.velocidad,
               volumen=args.volumen, oir=args.oir)
    print("listo" if not wav else f"listo: {wav}")


def cmd_escuchar(args):
    from uremote.core import control, devices, registry
    nombre, datos = devices.obtener(args.tv)
    perfil = registry.cargar_perfil(datos["perfil"])
    mapa = {frase: tecla for frase, tecla in comandos.FRASES.items()
            if tecla in perfil["teclas"]}
    print(f"control por voz de '{nombre}' — frases:")
    print("  " + ", ".join(sorted(mapa)))
    print(f"  di «{comandos.FRASE_SALIR}» o Ctrl+C para terminar")

    def al_reconocer(frase):
        if frase == comandos.FRASE_SALIR:
            print("bye")
            return False
        try:
            print(f"  «{frase}» -> {control.enviar(nombre, mapa[frase])}")
        except Exception as e:
            print(f"  error: {e}")

    motor.escuchar(list(mapa) + [comandos.FRASE_SALIR], al_reconocer,
                   confianza=args.confianza)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="voz",
                                 description="voz para uremote: escuchar micrófono y leer txt")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("voces", help="lista las voces TTS instaladas")

    p = sub.add_parser("leer", help="lee un txt con voz tipo loquendo")
    p.add_argument("archivo")
    p.add_argument("--voz", default="", help="nombre de voz (ver `voz voces`)")
    p.add_argument("--wav", nargs="?", const="AUTO", default="",
                   help="generar wav en silencio; sin ruta lo pone junto al txt")
    p.add_argument("--oir", action="store_true",
                   help="con --wav: además reproducirlo al terminar")
    p.add_argument("--velocidad", type=int, default=0, help="-10 a 10")
    p.add_argument("--volumen", type=int, default=100, help="0 a 100")

    p = sub.add_parser("escuchar", help="micrófono -> comandos a la tele")
    p.add_argument("--tv")
    p.add_argument("--confianza", type=float, default=0.5,
                   help="0 a 1; más alto = más estricto (default 0.5)")

    args = ap.parse_args(argv)
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
