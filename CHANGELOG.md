# Changelog

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
