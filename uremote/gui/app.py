"""Control gráfico. Los botones salen del layout del perfil (aparecen y
desaparecen según la marca) y cada click hace eco del comando CLI
equivalente en la consola integrada, donde también se puede teclear."""

import os
import threading
import tkinter as tk
from tkinter import ttk

from uremote import theme
from uremote.core import control, devices, macros, paths, registry


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("uremote")
        raiz.configure(bg=theme.FONDO)

        self._barra()
        cuerpo = tk.Frame(raiz, bg=theme.FONDO)
        cuerpo.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.panel_control = tk.Frame(cuerpo, bg=theme.FONDO)
        self.panel_control.pack(side="left", fill="y", padx=(0, 6))
        self._consola(cuerpo)
        self._atajos()
        self._recargar_tvs()
        self.eco("uremote gui  |  escribe comandos abajo (ej: mandar vol+)", "eco")

    # ------------------------------------------------ barra superior
    def _barra(self):
        barra = tk.Frame(self.raiz, bg=theme.FONDO)
        barra.pack(fill="x", padx=6, pady=6)
        tk.Label(barra, text="TV:", bg=theme.FONDO, fg=theme.BTN_FG).pack(side="left")
        self.combo_tv = ttk.Combobox(barra, state="readonly", width=14)
        self.combo_tv.pack(side="left", padx=4)
        self.combo_tv.bind("<<ComboboxSelected>>", lambda e: self._cambiar_tv())
        ttk.Button(barra, text="✕", width=3, command=self._quitar_tv).pack(side="left")
        ttk.Button(barra, text="↻", width=3, command=self._recargar_tvs).pack(side="left")
        ttk.Button(barra, text="enlazar", command=self._enlazar).pack(side="left", padx=4)
        ttk.Button(barra, text="manual", command=self._manual).pack(side="left")
        ttk.Button(barra, text="macro ▶", command=self._correr_macro).pack(side="left")
        self.btn_rec = tk.Button(barra, text="● rec", fg=theme.REC_OFF,
                                 relief="flat", bg=theme.FONDO,
                                 activebackground=theme.FONDO,
                                 command=self._alternar_rec)
        self.btn_rec.pack(side="right")

    # ------------------------------------------------ consola
    def _consola(self, padre):
        marco = tk.Frame(padre, bg=theme.CONSOLA_BG)
        marco.pack(side="left", fill="both", expand=True)
        self.texto = tk.Text(marco, bg=theme.CONSOLA_BG, fg=theme.CONSOLA_FG,
                             insertbackground=theme.CONSOLA_FG,
                             font=("Consolas", 9), width=52, height=28,
                             state="disabled", relief="flat")
        self.texto.pack(fill="both", expand=True, padx=4, pady=4)
        self.texto.tag_config("err", foreground=theme.CONSOLA_ERR)
        self.texto.tag_config("eco", foreground=theme.CONSOLA_ECO)
        self.entrada = tk.Entry(marco, bg=theme.CONSOLA_BG, fg=theme.CONSOLA_FG,
                                insertbackground=theme.CONSOLA_FG,
                                font=("Consolas", 9), relief="flat")
        self.entrada.pack(fill="x", padx=4, pady=(0, 4))
        self.entrada.bind("<Return>", self._comando_tecleado)

    def eco(self, linea, tag=None):
        self.texto.configure(state="normal")
        self.texto.insert("end", linea + "\n", tag)
        self.texto.see("end")
        self.texto.configure(state="disabled")

    # ------------------------------------------------ control por perfil
    def _tv_actual(self):
        return self.combo_tv.get() or None

    def _recargar_tvs(self):
        tvs = list(devices.lista())
        self.combo_tv["values"] = tvs
        defecto = devices.por_defecto()
        if defecto in tvs:
            self.combo_tv.set(defecto)
        elif tvs:
            self.combo_tv.set(tvs[0])
        self._cambiar_tv()

    def _quitar_tv(self):
        tv = self._tv_actual()
        if not tv:
            return
        devices.quitar(tv)
        self.eco(f"> uremote tvs quitar {tv}", "eco")
        self._recargar_tvs()

    def _cambiar_tv(self):
        for hijo in self.panel_control.winfo_children():
            hijo.destroy()
        tv = self._tv_actual()
        if not tv:
            tk.Label(self.panel_control, text="sin TVs\nusa: tvs agregar ...",
                     bg=theme.FONDO, fg=theme.SECCION_FG).pack(pady=20)
            return
        perfil = registry.cargar_perfil(devices.lista()[tv]["perfil"])
        for seccion in perfil["layout"]:
            marco = tk.LabelFrame(self.panel_control, text=seccion["titulo"],
                                  bg=theme.FONDO, fg=theme.SECCION_FG,
                                  font=("Segoe UI", 8))
            marco.pack(fill="x", pady=2)
            for f, fila in enumerate(seccion["filas"]):
                for c, tecla in enumerate(fila):
                    if not tecla:
                        continue
                    bg, fg = theme.BTN_ACCION.get(tecla, (theme.BTN_BG, theme.BTN_FG))
                    tk.Button(marco, text=tecla, width=7, bg=bg, fg=fg,
                              relief="groove", font=("Segoe UI", 8),
                              command=lambda t=tecla: self._click(t)
                              ).grid(row=f, column=c, padx=1, pady=1)

    # ------------------------------------------------ acciones
    def _en_hilo(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def _click(self, tecla):
        tv = self._tv_actual()
        self.eco(f"> uremote mandar {tecla} --tv {tv}", "eco")

        def trabajo():
            try:
                r = control.enviar(tv, tecla)
                self.raiz.after(0, lambda: self.eco(r))
            except Exception as e:
                msg = f"error: {e}"
                self.raiz.after(0, lambda m=msg: self.eco(m, "err"))
        self._en_hilo(trabajo)

    def _comando_tecleado(self, _evento):
        linea = self.entrada.get().strip()
        if not linea:
            return
        self.entrada.delete(0, "end")
        self.eco(f"> uremote {linea}", "eco")
        partes = linea.split()

        def trabajo():
            try:
                if partes[0] in ("mandar", "texto"):
                    control.ejecutar_linea(partes, self._tv_actual())
                    self.raiz.after(0, lambda: self.eco("ok"))
                elif partes[0] == "espera":
                    import time
                    time.sleep(float(partes[1]))
                else:
                    raise ValueError("aquí sólo: mandar / texto / espera")
            except Exception as e:
                msg = f"error: {e}"
                self.raiz.after(0, lambda m=msg: self.eco(m, "err"))
        self._en_hilo(trabajo)

    def _alternar_rec(self):
        if devices.grabando():
            nombre = devices.grabando()
            devices.grabando(None)
            self.btn_rec.configure(fg=theme.REC_OFF)
            self.eco(f"> uremote macro fin  ({nombre})", "eco")
        else:
            nombre = _pedir(self.raiz, "nombre de la macro a grabar:")
            if not nombre:
                return
            devices.grabando(nombre)
            self.btn_rec.configure(fg=theme.REC_ON)
            self.eco(f"> uremote macro grabar {nombre}", "eco")

    def _correr_macro(self):
        disponibles = macros.lista()
        if not disponibles:
            self.eco("sin macros grabadas", "err")
            return
        nombre = _pedir(self.raiz, f"macro a correr ({', '.join(disponibles)}):")
        if not nombre:
            return
        tv = self._tv_actual()
        self.eco(f"> uremote macro correr {nombre} --tv {tv}", "eco")

        def trabajo():
            try:
                macros.correr(nombre,
                              lambda p: control.ejecutar_linea(p, tv),
                              eco=lambda l: self.raiz.after(0, lambda l=l: self.eco(f"  > {l}")))
                self.raiz.after(0, lambda: self.eco("macro terminada"))
            except Exception as e:
                msg = f"error: {e}"
                self.raiz.after(0, lambda m=msg: self.eco(m, "err"))
        self._en_hilo(trabajo)

    def _enlazar(self):
        """Descubre dispositivos en la red y los agrega con un click."""
        import re
        from uremote import discover
        dialogo = tk.Toplevel(self.raiz)
        dialogo.title("enlazar dispositivo")
        dialogo.configure(bg=theme.FONDO)
        dialogo.transient(self.raiz)
        aviso = tk.Label(dialogo, text="buscando en la red...",
                         bg=theme.FONDO, fg=theme.SECCION_FG)
        aviso.pack(padx=14, pady=10)
        self.eco("> uremote descubrir", "eco")

        def pintar(halladas):
            aviso.destroy()
            utiles = [tv for tv in halladas if tv["perfil"] != "?"]
            otros = [tv for tv in halladas if tv["perfil"] == "?"]
            if not utiles:
                tk.Label(dialogo, text="no encontré TVs compatibles\n"
                         "(¿prendida y en el mismo WiFi?)",
                         bg=theme.FONDO, fg=theme.SECCION_FG).pack(padx=14, pady=6)
            for tv in utiles:
                fila = tk.Frame(dialogo, bg=theme.FONDO)
                fila.pack(fill="x", padx=10, pady=3)
                etiqueta = tv["nombre"] or tv["server"][:30] or tv["ip"]
                if tv["modelo"]:
                    etiqueta += f"  ({tv['modelo']})"
                tk.Label(fila, text=f"{etiqueta}\n{tv['ip']}  ·  {tv['perfil']}",
                         bg=theme.FONDO, fg=theme.BTN_FG, justify="left",
                         font=("Segoe UI", 9)).pack(side="left")
                sugerido = re.sub(r"[^a-z0-9]+", "_",
                                  (tv["nombre"] or tv["perfil"]).lower()).strip("_")[:12]
                ya = sugerido in devices.lista()
                boton = ttk.Button(fila, text="agregada ✓" if ya else "agregar")
                boton.configure(command=lambda t=tv, n=sugerido, b=boton:
                                self._agregar_tv(t, n, b))
                if ya:
                    boton.state(["disabled"])
                boton.pack(side="right", padx=6)
            if otros:
                tk.Label(dialogo, text="otros (sin perfil conocido): "
                         + ", ".join(t["ip"] for t in otros),
                         bg=theme.FONDO, fg=theme.SECCION_FG,
                         font=("Segoe UI", 8)).pack(padx=10, pady=(6, 10))

        def trabajo():
            halladas = discover.buscar(2)
            self.raiz.after(0, lambda: pintar(halladas))
        self._en_hilo(trabajo)

    def _agregar_tv(self, tv, nombre, boton):
        devices.agregar(nombre, tv["ip"], tv["perfil"])
        self.eco(f"> uremote tvs agregar {nombre} {tv['ip']} {tv['perfil']}", "eco")
        self.eco(f"enlazada: {nombre}")
        boton.configure(text="agregada ✓")
        boton.state(["disabled"])
        self._recargar_tvs()
        self.combo_tv.set(nombre)
        self._cambiar_tv()

    def _manual(self):
        tv = self._tv_actual()
        if not tv:
            return
        perfil = registry.cargar_perfil(devices.lista()[tv]["perfil"])
        consulta = perfil["manual_busqueda"]
        if consulta.startswith("http"):  # doc web-only: abrir directo
            self.eco(f"documentación en línea: {consulta}", "eco")
            import webbrowser
            webbrowser.open(consulta)
            return
        ya = list(paths.MANUALES.glob("*.pdf")) if paths.MANUALES.exists() else []
        local = [p for p in ya if all(w in p.stem for w in consulta.lower().split()[:2])]
        if local:
            self.eco(f"abriendo {local[0].name}", "eco")
            os.startfile(local[0])
            return
        self.eco(f"> uremote manual --abrir  (buscando: {consulta})", "eco")

        portal = perfil.get("manual_portal")

        def trabajo():
            from manualhunt.hunt import buscar
            ruta, respaldo = buscar(consulta, paths.MANUALES,
                                    eco=lambda l: self.raiz.after(0, lambda l=l: self.eco(l)))
            destino = portal or respaldo
            if ruta:
                os.startfile(ruta)
            elif destino:
                origen = "portal oficial" if portal else "soporte"
                self.raiz.after(0, lambda: self.eco(f"sin PDF; abriendo {origen}: {destino[:70]}", "eco"))
                import webbrowser
                webbrowser.open(destino)
            else:
                self.raiz.after(0, lambda: self.eco("no encontré el manual", "err"))
        self._en_hilo(trabajo)

    # ------------------------------------------------ teclado físico
    def _atajos(self):
        mapa = {"<Up>": "arriba", "<Down>": "abajo", "<Left>": "izq",
                "<Right>": "der", "<Return>": "ok", "<BackSpace>": "atras",
                "<Prior>": "ch+", "<Next>": "ch-",
                "<plus>": "vol+", "<minus>": "vol-"}
        for secuencia, tecla in mapa.items():
            self.raiz.bind(secuencia, lambda e, t=tecla: self._atajo(t))

    def _atajo(self, tecla):
        if self.raiz.focus_get() is self.entrada:
            return
        tv = self._tv_actual()
        if not tv:
            return
        perfil = registry.cargar_perfil(devices.lista()[tv]["perfil"])
        if tecla in perfil["teclas"]:
            self._click(tecla)


def _pedir(raiz, mensaje):
    from tkinter import simpledialog
    return simpledialog.askstring("uremote", mensaje, parent=raiz)


def correr():
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
