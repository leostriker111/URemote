# Changelog

## 0.4.0 — 2026-07-08
- **`uremote frase`**: la frase viaja cruda al buscador nativo de la tele (Roku ECP,
  Android TV Assistant) y ella la interpreta; intents solo como comandos de control
  conocidos y fallback para teles sin buscador. Guiones y agenda pasan por aquí.
- **Condiciones enchufables** en la agenda: 1 archivo = 1 condición
  (`hora`, `arranque`, `tv_encendida`), encadenables con Y (`--cuando`, repetible);
  `agenda condiciones` las lista. Migración automática del formato viejo.
- **Confirmación por toast** de Windows con botones va / ahora no (protocolo
  `uremote://` en HKCU); fuera la ventanita Tk.
- **Drivers Samsung Tizen y LG webOS** (websocket, pairing en pantalla, token/llave
  persistida) con dependencia opcional: `pip install uremote[samsung]` / `[lg]`.
- **Perfiles de usuario** en `config/perfiles/` (pisan a los del paquete); el
  descubrimiento reconoce Samsung/LG; perfiles declaran `puerto`.
- GUI: selector "de archivo…" en la agenda (elige guion y su instrucción numerada).

## 0.3.x — 2026-07-08
- Guiones numerados (`//nota` + `N"frase";`), intents, agenda programada con tarea
  de Windows cada minuto, botones guion/agenda en la GUI.

## 0.2.0 — 2026-07-08
- Botón **enlazar** en la GUI: descubre TVs por SSDP, jala nombre/modelo real por UPnP y agrega con un click; ✕ para quitar del combo.
- Sub-herramienta **voz/**: control por voz con el micrófono (gramática en español, offline) y lectura de txt con TTS (`--wav` silencioso, `--oir`, `--volumen`, `--velocidad`).
- `app`: abre apps en la tele (Netflix, YouTube...) con deep-link a título directo en Roku.
- Manuales: portal oficial por marca (`manual_portal`), página de soporte de respaldo, `-a` para elegir carpeta.
- Errores accionables por driver (Roku 403, Android TV sin depuración).
- Empaquetado pip + installer; datos en `~/.uremote` cuando está instalado.

## 0.1.0 — 2026-07-07
- CLI + GUI tkinter; drivers Panasonic Viera (SOAP), Roku (ECP), Android TV (adb).
- Perfiles JSON por marca (teclas + layout), descubrimiento SSDP, macros grabables,
  archivos de estatus por TV, manualhunt (cazador de manuales PDF), selftest.
