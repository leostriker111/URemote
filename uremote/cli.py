"""CLI de uremote. Cada subcomando es una función cmd_*."""

import argparse
import json
import os
import sys

from uremote.core import control, devices, macros, paths, registry, state


def cmd_descubrir(args):
    from uremote import discover
    print("buscando TVs en la red (SSDP)...")
    halladas = discover.buscar(args.segundos)
    if not halladas:
        print("nada; ¿la tele está prendida y en el mismo WiFi?")
        return
    for tv in halladas:
        etiqueta = tv["nombre"] or tv["server"][:40]
        modelo = f" ({tv['modelo']})" if tv["modelo"] else ""
        print(f"  {tv['ip']:<15} perfil: {tv['perfil']:<16} {etiqueta}{modelo}")
    print("agrega con: uremote tvs agregar <nombre> <ip> <perfil>")


def cmd_tvs(args):
    if args.accion == "lista" or args.accion is None:
        defecto = devices.por_defecto()
        for nombre, d in devices.lista().items():
            marca = "*" if nombre == defecto else " "
            print(f"{marca} {nombre:<12} {d['ip']:<15} {d['perfil']}")
        if not devices.lista():
            print("sin TVs; usa: uremote tvs agregar <nombre> <ip> <perfil>")
    elif args.accion == "agregar":
        registry.cargar_perfil(args.perfil)  # valida
        devices.agregar(args.nombre, args.ip, args.perfil)
        print(f"agregada: {args.nombre} ({args.ip}, {args.perfil})")
    elif args.accion == "quitar":
        devices.quitar(args.nombre)
        print(f"quitada: {args.nombre}")
    elif args.accion == "defecto":
        devices.por_defecto(args.nombre)
        print(f"por defecto: {args.nombre}")


def cmd_mandar(args):
    for tecla in args.teclas:
        print(control.enviar(args.tv, tecla))


def cmd_texto(args):
    print(control.escribir(args.tv, " ".join(args.palabras)))


def cmd_app(args):
    print(control.abrir_app(args.tv, args.app, args.contenido, args.tipo))


def cmd_teclas(args):
    if args.perfil:
        perfil = registry.cargar_perfil(args.perfil)
    else:
        _, datos = devices.obtener(args.tv)
        perfil = registry.cargar_perfil(datos["perfil"])
    print(f"{perfil['nombre']}:")
    for seccion in perfil["layout"]:
        presentes = [t for fila in seccion["filas"] for t in fila if t]
        print(f"  [{seccion['titulo']}] {' '.join(presentes)}")


def cmd_perfiles(args):
    for nombre in registry.lista_perfiles():
        p = registry.cargar_perfil(nombre)
        print(f"  {nombre:<18} {p['nombre']} ({len(p['teclas'])} teclas)")


def cmd_macro(args):
    if args.accion == "lista":
        for m in macros.lista():
            print(f"  {m}")
        if not macros.lista():
            print("sin macros; graba con: uremote macro grabar <nombre>")
    elif args.accion == "ver":
        print(macros.ver(args.nombre), end="")
    elif args.accion == "grabar":
        devices.grabando(args.nombre)
        print(f"grabando '{args.nombre}': cada `uremote mandar` se anota. "
              "Termina con: uremote macro fin")
    elif args.accion == "fin":
        nombre = devices.grabando()
        devices.grabando(None)
        print(f"grabación terminada: {nombre or '(no había)'}")
    elif args.accion == "correr":
        macros.correr(args.nombre,
                      lambda partes: control.ejecutar_linea(partes, args.tv),
                      eco=lambda l: print(f"  > {l}"))
        print(f"macro '{args.nombre}' terminada")


def cmd_estado(args):
    if args.accion == "leer" or args.accion is None:
        nombre, _ = devices.obtener(args.tv)
        datos = control.consultar(args.tv) if args.vivo else state.leer(nombre)
        print(json.dumps(datos, indent=2, ensure_ascii=False))
    elif args.accion == "set":
        nombre, _ = devices.obtener(args.tv)
        state.poner_campo(nombre, args.clave, args.valor)
        print(f"{nombre}.campos.{args.clave} = {args.valor}")


def cmd_manual(args):
    from manualhunt.hunt import buscar
    perfil = None
    if args.consulta:
        palabras = args.consulta[1:] if args.consulta[0] == "buscar" else args.consulta
        consulta = " ".join(palabras)
    else:
        _, datos = devices.obtener(args.tv)
        perfil = registry.cargar_perfil(datos["perfil"])
        consulta = perfil["manual_busqueda"]
    if consulta.startswith("http"):  # doc web-only: abrir directo
        print(f"documentación en línea: {consulta}")
        import webbrowser
        webbrowser.open(consulta)
        return
    from pathlib import Path
    carpeta = Path(args.carpeta) if args.carpeta else paths.MANUALES
    ya = list(carpeta.glob("*.pdf")) if carpeta.exists() else []
    coincide = [p for p in ya if all(w in p.stem for w in consulta.lower().split()[:2])]
    if coincide and not args.forzar:
        ruta = coincide[0]
        print(f"ya descargado: {ruta}")
    else:
        print(f"buscando manual: {consulta}")
        ruta, respaldo = buscar(consulta, carpeta)
        if ruta is None:
            portal = perfil.get("manual_portal") if perfil else None
            destino = portal or respaldo
            if destino:
                origen = "portal oficial de la marca" if portal else "página de soporte"
                print(f"sin PDF directo; {origen}: {destino}")
                if args.abrir:
                    import webbrowser
                    webbrowser.open(destino)
            else:
                print("no encontré nada; intenta: uremote manual buscar <otras palabras>")
            return
    if args.abrir:
        os.startfile(ruta)


def cmd_guion(args):
    from uremote.core import guion
    if args.numero is None:
        for n, e in sorted(guion.cargar(args.archivo).items()):
            nota = f"  // {e['nota']}" if e["nota"] else ""
            print(f"  {n}: \"{e['frase']}\"{nota}")
    else:
        print(guion.correr(args.archivo, args.numero, args.tv))


def cmd_agenda(args):
    from uremote.core import agenda
    if args.accion == "lista" or args.accion is None:
        for e in agenda.lista():
            estado = "⏸" if e["pausada"] else "●"
            print(f"  {estado} [{e['id']}] {e['hora']} {e['dias']:<10} "
                  f"{e['modo']:<9} {e['accion']}")
        if not agenda.lista():
            print("agenda vacía; usa: uremote agenda agregar HH:MM --hacer \"...\"")
    elif args.accion == "agregar":
        nid = agenda.agregar(args.hora, args.hacer, dias=args.dias, tv=args.tv,
                             modo="confirmar" if args.confirmar else "solo",
                             anunciar=args.anunciar,
                             notificar=not args.sin_notificar)
        print(f"programada [{nid}]: {args.hora} {args.dias} -> {args.hacer}")
    elif args.accion == "quitar":
        agenda.quitar(args.hora)  # aquí el 2o arg es el id
        print("quitada")
    elif args.accion == "pausar":
        print(agenda.pausar(args.hora))
    elif args.accion == "tick":
        agenda.tick()
    elif args.accion == "instalar":
        print(f"tarea de Windows registrada: {agenda.instalar()} (cada minuto)")
    elif args.accion == "desinstalar":
        agenda.desinstalar()
        print("tarea quitada")
    elif args.accion == "log":
        if agenda.LOG.exists():
            print(agenda.LOG.read_text(encoding="utf-8"), end="")


def cmd_voz(args):
    from voz.__main__ import main as voz_main
    voz_main(args.resto or ["-h"])


def cmd_gui(args):
    from uremote.gui.app import correr
    correr()


def cmd_selftest(args):
    from uremote.drivers import dummy
    devices.agregar("_test", "0.0.0.0", "dummy")
    control.enviar("_test", "vol+")
    control.enviar("_test", "power")
    assert dummy.ENVIADO == ["VOLUP", "POWER"], dummy.ENVIADO
    assert state.leer("_test")["ultima_tecla"] == "power"
    devices.grabando("_testmacro")
    control.enviar("_test", "ok")
    devices.grabando(None)
    macros.anotar("_testmacro", "espera 0.1")
    macros.correr("_testmacro", lambda p: control.ejecutar_linea(p, "_test"))
    assert dummy.ENVIADO[-1] == "OK"
    assert control.consultar("_test")["volumen"] == 15
    # limpieza
    devices.quitar("_test")
    (paths.MACROS / "_testmacro.txt").unlink()
    (paths.ESTADOS / "_test.json").unlink()
    print("selftest OK: enviar, estado, macro grabar/correr, consulta en vivo")


def main():
    ap = argparse.ArgumentParser(prog="uremote",
                                 description="control remoto universal para smart TVs")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("descubrir", help="busca TVs en la red")
    p.add_argument("-s", "--segundos", type=int, default=3)

    p = sub.add_parser("tvs", help="administra TVs configuradas")
    p.add_argument("accion", nargs="?", choices=["lista", "agregar", "quitar", "defecto"])
    p.add_argument("nombre", nargs="?")
    p.add_argument("ip", nargs="?")
    p.add_argument("perfil", nargs="?")

    p = sub.add_parser("mandar", help="manda una o más teclas")
    p.add_argument("teclas", nargs="+")
    p.add_argument("--tv")

    p = sub.add_parser("texto", help="escribe texto en la tele (si la marca puede)")
    p.add_argument("palabras", nargs="+")
    p.add_argument("--tv")

    p = sub.add_parser("app", help="abre una app en la tele (netflix, youtube...)")
    p.add_argument("app", help="alias del perfil o id directo")
    p.add_argument("--contenido", default="", help="id del título para abrirlo directo")
    p.add_argument("--tipo", default="", help="movie | series | episode")
    p.add_argument("--tv")

    p = sub.add_parser("teclas", help="lista las teclas del perfil activo")
    p.add_argument("--tv")
    p.add_argument("--perfil")

    sub.add_parser("perfiles", help="lista las marcas/modelos disponibles")

    p = sub.add_parser("macro", help="graba, ve y corre macros")
    p.add_argument("accion", choices=["lista", "ver", "grabar", "fin", "correr"])
    p.add_argument("nombre", nargs="?")
    p.add_argument("--tv")

    p = sub.add_parser("estado", help="archivo de estatus de la tele")
    p.add_argument("accion", nargs="?", choices=["leer", "set"])
    p.add_argument("clave", nargs="?")
    p.add_argument("valor", nargs="?")
    p.add_argument("--tv")
    p.add_argument("--vivo", action="store_true", help="consulta a la tele en vivo")

    p = sub.add_parser("manual", help="descarga/abre el manual de la tele")
    p.add_argument("consulta", nargs="*", help="búsqueda libre (vacío = la del perfil)")
    p.add_argument("--tv")
    p.add_argument("--abrir", action="store_true")
    p.add_argument("--forzar", action="store_true", help="re-descargar")
    p.add_argument("-a", "--carpeta", help="carpeta destino (default: manuales/)")

    p = sub.add_parser("guion", help="txt con comandos de voz numerados")
    p.add_argument("archivo")
    p.add_argument("numero", nargs="?", type=int, help="vacío = listar el menú")
    p.add_argument("--tv")

    p = sub.add_parser("agenda", help="programa comandos por hora/días")
    p.add_argument("accion", nargs="?",
                   choices=["lista", "agregar", "quitar", "pausar", "tick",
                            "instalar", "desinstalar", "log"])
    p.add_argument("hora", nargs="?", help="HH:MM (o id en quitar/pausar)")
    p.add_argument("--hacer", help='frase o "guion archivo N"')
    p.add_argument("--dias", default="diario", help="diario | lun-vie | sab,dom")
    p.add_argument("--tv")
    p.add_argument("--confirmar", action="store_true",
                   help="pedir ventanita antes de ejecutar (60s o se cancela)")
    p.add_argument("--anunciar", action="store_true", help="Sabina lo anuncia")
    p.add_argument("--sin-notificar", action="store_true")

    p = sub.add_parser("voz", help="control por voz y lectura de txt (ver: uremote voz -h)")
    p.add_argument("resto", nargs=argparse.REMAINDER)

    sub.add_parser("gui", help="abre el control gráfico")
    sub.add_parser("selftest", help="prueba end-to-end con driver falso")

    args = ap.parse_args()
    if args.cmd is None:
        ap.print_help()
        return
    try:
        globals()[f"cmd_{args.cmd}"](args)
    except (ValueError, RuntimeError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
