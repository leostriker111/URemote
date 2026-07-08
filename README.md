# uremote

**Control remoto universal para smart TVs por WiFi.** CLI + GUI, Python puro, cero dependencias.

Un solo comando controla tu Panasonic Viera, Roku o Android TV desde la terminal o desde una
interfaz gráfica que se adapta a cada marca: los botones que dibuja salen del perfil de la tele,
así que sólo ves los que tu tele entiende.

```
uremote descubrir                 # encuentra las TVs de tu red y te dice qué son
uremote mandar vol+ ch+ ok        # manda teclas en cadena
uremote app netflix               # abre apps (con deep-link a títulos en Roku)
uremote gui                       # el control gráfico
```

## Características

- **Descubrimiento automático** (SSDP/UPnP): encuentra las TVs, jala su nombre y modelo real,
  y en la GUI se enlazan con un click.
- **Perfiles por marca**: agregar una tele nueva = 1 archivo JSON (teclas + layout) y, si el
  protocolo es nuevo, 1 driver de ~50 líneas. Nada más.
- **Macros grabables**: `macro grabar noche`, aprietas botones, `macro fin` — queda un `.txt`
  editable que reproduce toda la secuencia (con `espera N` entre pasos).
- **Archivos de estatus** por TV: última tecla, última entrada, volumen real (donde el
  protocolo lo permite) y campos libres (`estado set perfil_imagen cine`).
- **Control por voz** (Windows, offline): `uremote voz escuchar` — el micrófono oye
  "sube volumen", "canal arriba"... y la tele obedece. Gramática cerrada en español.
- **Lectura TTS**: `uremote voz leer notas.txt` habla el archivo; `--wav` lo genera en
  silencio, `--oir` lo guarda y lo reproduce.
- **Cazador de manuales**: `uremote manual --abrir` busca el PDF del manual de tu tele,
  lo valida y lo descarga; si la marca ya no publica PDF, abre su portal oficial.
- **Errores que ayudan**: si la tele rechaza la conexión, el mensaje te dice exactamente
  qué menú activar (ej. Roku: Control por aplicaciones móviles).

## Instalación

### pip (recomendada)
```
pip install git+https://github.com/leostriker111/uremote
```
Deja `uremote` y `manualhunt` disponibles en cmd/PowerShell directamente.

### Script rápido (portable)
```powershell
irm https://raw.githubusercontent.com/leostriker111/uremote/main/get-uremote.ps1 | iex
```
Clona a `~\URemote` y agrega la carpeta al PATH del usuario.

### Installer (.exe)
Descarga `uremote-setup.exe` de la página de
[releases](https://github.com/leostriker111/uremote/releases); instala y agrega el PATH solo.

## Protocolos soportados

| Marca | Protocolo | Notas |
|---|---|---|
| Panasonic Viera (2011-2017) | SOAP/UPnP :55000 | sin pairing; lee volumen/mute reales |
| Roku / Roku TV | ECP :8060 | apps con deep-link, texto, app activa |
| Android TV / Google TV | adb :5555 | requiere depuración por red |

## Uso

```
uremote descubrir                          # ¿qué hay en la red?
uremote tvs agregar sala 192.168.1.185 panasonic_viera
uremote teclas                             # qué botones tiene tu perfil
uremote mandar power                       # y todos los demás botones
uremote texto hola                         # teclea en la tele (Roku/Android)
uremote app youtube --tv sala
uremote macro grabar ajuste_noche ... uremote macro fin
uremote macro correr ajuste_noche
uremote estado leer --vivo
uremote manual --abrir
uremote voz escuchar                       # di "ya estuvo" para terminar
uremote voz leer guion.txt --wav --oir
uremote gui
```

En la GUI, la consola integrada muestra el comando CLI equivalente de cada botón que
aprietas — el control gráfico también te enseña a usar la terminal.

## Agregar una marca nueva

1. Copia un perfil de `uremote/profiles/` y ajusta teclas/layout al modelo nuevo.
2. Si usa un protocolo que ya existe (ECP, SOAP Viera, adb) ya quedó.
3. Si no, crea `uremote/drivers/mimarca.py` con una clase `Driver(Base)` que implemente
   `mandar(codigo)` — y atrapa el error típico de conexión con un mensaje que diga cómo
   destrabarla en el menú de la tele.
4. `uremote selftest` para verificar que no rompiste el motor.

## Licencia

MIT — [Leostriker](https://github.com/leostriker111)
