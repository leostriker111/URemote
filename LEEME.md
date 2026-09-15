<p align="center">
  <a href="README.md">English</a> · <b>Español</b>
</p>

<div align="center">

<img src="recursos/uremote.svg" width="104" alt="URemote">

# URemote

### Un control para todas las teles de tu WiFi. Sin nube, sin cuenta, sin app.

Encuentra las televisiones de tu red, averigua qué son, y las maneja — desde la
terminal o desde una ventana cuyos botones **se construyen del perfil de tu
propia tele**, así que sólo ves los que entiende.

[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-2c7a51?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pruebas](https://img.shields.io/github/actions/workflow/status/leostriker111/URemote/ci.yml?branch=main&style=flat-square&label=pruebas)](../../actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/leostriker111/URemote?style=flat-square&label=descargar)](../../releases)
![Sin dependencias](https://img.shields.io/badge/dependencias-ninguna-0e9f6e?style=flat-square)

</div>

---

## Qué es

Una **herramienta de línea de comandos** y un **control gráfico**, el mismo
programa de las dos formas. Le habla directo al protocolo de red de cada marca —
sin la nube del fabricante, sin cuenta, sin una app del celular en medio, y sin
que nada salga de tu red local.

La idea de diseño es que **una tele es un perfil, no un caso especial**. Agregar
una televisión significa escribir un archivo JSON con sus teclas y su acomodo de
botones. Sólo si el protocolo es nuevo escribes código, y son como cincuenta
líneas.

En la práctica se ve así:

```bash
uremote descubrir                 # encuentra las TVs de tu red y te dice que son
uremote mandar vol+ ch+ ok        # manda teclas en cadena
uremote app netflix               # abre apps (con deep-link a titulos en Roku)
uremote gui                       # el control grafico
```

## Propósito y alcance

**El propósito.** Dejar de perder el control. Y también volver la televisión algo
que un script pueda manejar: si `uremote mandar power` es un comando, entonces
apagar la tele a medianoche es una tarea programada y no una disciplina.

**Qué abarca.** Descubrimiento, teclas, escribir texto, apps, macros grabables,
archivos de estado por tele, una agenda con condiciones enchufables, control por
voz sin conexión, y un cazador que va y encuentra el manual en PDF de tu tele.

**Qué no hace.** Nada de nube, nada de acceso desde fuera de tu red, nada de
cuenta. Si no estás en el mismo WiFi, no te puede ayudar — ése es el precio de no
depender del servidor de nadie.

## Contenido

- [Qué es](#qué-es) · [Propósito y alcance](#propósito-y-alcance)
- [Instalación](#instalación) · [Protocolos soportados](#protocolos-soportados)
- [Cómo se empieza (CLI)](#cómo-se-empieza-cli)
- [La agenda](#la-agenda) · [Control por voz](#control-por-voz)
- [El control gráfico](#el-control-gráfico)
- [Agregar una marca nueva](#agregar-una-marca-nueva)
- [Para quien quiera meter mano](#contribuir)

## Instalación

**pip** — deja `uremote` y `manualhunt` disponibles en cmd y PowerShell:

```bash
pip install git+https://github.com/leostriker111/URemote
```

**Script portable** — clona a `~\URemote` y lo agrega a tu `PATH` de usuario:

```powershell
irm https://raw.githubusercontent.com/leostriker111/URemote/main/get-uremote.ps1 | iex
```

**Instalador** — baja `uremote-setup.exe` de [Releases](../../releases).

## Protocolos soportados

| marca | protocolo | estado |
|---|---|---|
| **Panasonic Viera** (2011-2017) | SOAP/UPnP `:55000` | ✅ Probado. Sin pairing; lee volumen y mute reales |
| **Roku / Roku TV** | ECP `:8060` | ✅ Probado. Apps con deep-link, texto, app activa |
| **Android TV / Google TV** | adb `:5555` | ✅ Probado. Necesita depuración por red encendida |
| **LG webOS** | websocket de webOS | ⚠️ Driver escrito, **nunca probado contra una tele** |
| **Samsung Tizen** | websocket de Tizen | ⚠️ Driver escrito, **nunca probado contra una tele** |

Esos dos sin probar son justo donde más ayudaría una contribución — ver
[Contribuir](#contribuir).

## Cómo se empieza (CLI)

### Encontrar y registrar una tele

```bash
uremote descubrir                                    # ¿que hay en la red?
uremote tvs agregar sala 192.168.1.185 panasonic_viera
uremote teclas                                       # que botones trae este perfil
```

El descubrimiento es SSDP/UPnP: encuentra las teles, les saca su nombre y modelo
reales, y en la GUI se enlazan con un clic.

### Manejarla

| comando | qué hace |
|---|---|
| `uremote mandar power` | Cualquier botón del perfil. En cadena: `mandar vol+ vol+ ok`. |
| `uremote texto hola` | Teclea en la tele (Roku y Android). |
| `uremote app youtube --tv sala` | Abre una app; en Roku puede ir directo a un título. |
| `uremote estado leer --vivo` | El archivo de estado: última tecla, última entrada, volumen real donde el protocolo lo da. |
| `uremote estado set perfil_imagen cine` | Campos libres que tú defines. |
| `uremote manual --abrir` | **Encuentra el manual de tu tele.** Busca el PDF, valida que sea el correcto, lo descarga — y si la marca ya no publica PDF, te abre su portal oficial. |
| `uremote selftest` | Comprueba que no rompiste el motor. |

### Macros

```bash
uremote macro grabar noche     # empezar a grabar
...                            # aprietas botones
uremote macro fin              # terminar
uremote macro correr noche     # reproducirla
```

Lo que queda es un `.txt` editable, no un binario opaco — `espera N` entre pasos
es nada más una línea que puedes agregar a mano.

## La agenda

Comandos que se disparan cuando se cumplen condiciones, encadenadas con Y:

```bash
uremote agenda instalar        # registra una tarea de Windows que hace tick cada minuto
```

Las entradas viven en `config/agenda.json`. Cada una trae una lista de
**condiciones**, y las condiciones son enchufables — un archivo cada una, en
`uremote/condiciones/`:

| condición | se cumple cuando |
|---|---|
| `hora` | llega cierta hora del día |
| `arranque` | arranca la computadora |
| `tv_encendida` | la tele está de verdad prendida |

Cada condición devuelve un **sello** que identifica *esta* ocurrencia, y la agenda
dispara una vez por sello. Eso es lo que evita que un tick cada minuto corra tu
entrada de «apaga todo» sesenta veces en una hora.

Escribir una condición nueva es un archivo que exponga `AYUDA` y
`se_cumple(params, entrada)`. Nada más tiene que enterarse de que existe.

## Control por voz

En Windows, y **completamente sin conexión**:

```bash
uremote voz escuchar           # di "ya estuvo" para terminar
```

El micrófono oye «sube volumen», «canal arriba» y los demás. La gramática es
cerrada y en español a propósito: un vocabulario fijo es lo que hace confiable el
reconocimiento sin un modelo en la nube.

También lee en voz alta:

```bash
uremote voz leer notas.txt          # habla el archivo
uremote voz leer guion.txt --wav    # lo genera como .wav, en silencio
uremote voz leer guion.txt --oir    # lo guarda y lo reproduce
```

## El control gráfico

```bash
uremote gui
```

Los botones se generan del perfil de la tele, así que una Viera y un Roku te dan
controles distintos y ninguno enseña una tecla que no haría nada.

El detalle que vale la pena: **la consola integrada imprime el comando de CLI
equivalente de cada botón que aprietas.** El control gráfico te enseña a usar la
terminal.

## Agregar una marca nueva

1. Copia un perfil de `uremote/profiles/` y ajusta teclas y acomodo.
2. Si usa un protocolo que ya existe (ECP, SOAP de Viera, adb), ya quedó.
3. Si no, crea `uremote/drivers/mimarca.py` con una clase `Driver(Base)` que
   implemente `mandar(codigo)` — y atrapa el error típico de conexión con un
   mensaje que diga qué menú activar en la tele.
4. Corre `uremote selftest`.

El paréntesis del paso 3 no es adorno. Todos estos protocolos rechazan la
conexión hasta que prendes algo en un menú de ajustes que nadie encuentra, y
**un buen mensaje de error es la mayor parte de lo que hace esto usable.**

<br>

---

<div align="center">

## 🔧 Para quien quiera meter mano

*Todo lo de arriba es lo que hace. Todo lo de abajo es cómo lo hace.*

</div>

---

### Contribuir

Lo más valioso, en orden:

1. **Probar los drivers de LG webOS y Samsung Tizen.** Están escritos y jamás han
   conocido una televisión de verdad. Si tienes una, un `uremote descubrir`
   seguido de un solo `uremote mandar power` ya nos dice algo que vale la pena
   saber.
2. **Marcas nuevas.** Vizio, Hisense, Chromecast. Casi siempre un archivo JSON.
3. **Control por voz en Linux y macOS** — el motor de `voz/motor.py` es la única
   parte del proyecto que depende de Windows.

**Y una idea más grande que estamos masticando:** una **extensión de navegador**,
para que manejar la tele no sea sólo cosa de terminal — pausar lo que está en la
pantalla grande desde la misma pestaña donde estás viendo otra cosa. No está
empezada, no está decidida la forma, y **de verdad preferiríamos oír opiniones
antes de escribir nada.** Si tienes una idea de cómo debería ser, abre un issue y
dila.

### De qué está hecho

**Python 3.8+ sin dependencias externas.** Todos estos protocolos son HTTP, SOAP,
SSDP o un websocket, y todos se alcanzan desde la librería estándar. No tener
dependencias es lo que permite repartirlo como una carpeta portable que dejas caer
en cualquier máquina.

### Los módulos

| área | módulos | qué hay |
|---|---|---|
| **drivers** | `panasonic_viera.py` 38 · `roku.py` 54 · `androidtv.py` 54 · `lg_webos.py` 86 · `samsung_tizen.py` 60 · `base.py` 24 · `dummy.py` 10 | Un archivo por protocolo, todos detrás de `Base.mandar(codigo)`. Los números de línea son el argumento del diseño por perfiles: una marca entera cabe en menos de sesenta líneas. |
| **core** | `agenda.py` 150 · `notifica.py` 79 · `control.py` 74 · `devices.py` 48 · `intents.py` 43 · `state.py` 40 · `macros.py` 38 · `guion.py` 29 · `registry.py` 24 · `paths.py` 16 | El motor: la agenda, el registro de teles conocidas, los archivos de estado, las macros. |
| **condiciones** | `hora.py` 17 · `tv_encendida.py` 22 · `arranque.py` 10 · `__init__.py` 18 | Las condiciones enchufables, cargadas por nombre con `importlib`. |
| **interfaces** | `cli.py` 292 · `gui/app.py` 416 · `discover.py` 69 · `theme.py` 22 | Las dos caras, más el descubrimiento por SSDP. |
| **voz** | `voz/motor.py` 88 · `voz/__main__.py` 61 · `voz/comandos.py` 32 | Reconocimiento y lectura, sólo Windows. |
| **manuales** | `manualhunt/hunt.py` 119 | Encontrar y validar el PDF. |

### La decisión que le dio forma

La manera obvia de escribir esto es una clase por televisión con un método por
botón. Es también como se vuelve inmantenible a la tercera marca, porque el 90 %
de esas clases es lo mismo y el 10 % que cambia queda enterrado.

Así que el corte es: **un perfil es datos y un driver es transporte.** Un perfil
es un JSON que lista qué teclas existen y cómo acomodarlas. Un driver sólo sabe
poner un código en el cable. La GUI lee el perfil para decidir qué dibujar, que es
por lo que nunca enseña un botón que la tele no puede hacer; y agregar una tele
que hable un protocolo que ya existe no toca ni una línea de Python.

Las condiciones de la agenda tienen la misma forma por la misma razón — un
archivo, un trabajo, descubierto por nombre.

### Licencia

[MIT](LICENSE) — [Leostriker](https://github.com/leostriker111).

### Proyectos relacionados

- **[Home Assistant](https://www.home-assistant.io/)** — *ése si quieres una casa
  inteligente entera;* URemote es un comando para televisiones, y va a seguir
  siendo un archivo que puedas leer.
- **`adb`** — sobre lo que se para el driver de Android TV. Si tu tele es Android
  y ya te llevas con adb, a lo mejor no necesitas esto.
