<p align="center">
  <b>English</b> · <a href="LEEME.md">Español</a>
</p>

<div align="center">

<img src="recursos/uremote.svg" width="104" alt="URemote">

# URemote

### One remote for every TV on your WiFi. No cloud, no account, no app.

Finds the televisions on your network, works out what they are, and drives them —
from the terminal or from a window whose buttons are **built from your TV's own
profile**, so you only ever see the ones it understands.

[![License: MIT](https://img.shields.io/badge/license-MIT-2c7a51?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/github/actions/workflow/status/leostriker111/URemote/ci.yml?branch=main&style=flat-square&label=tests)](../../actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/leostriker111/URemote?style=flat-square&label=download)](../../releases)
![No dependencies](https://img.shields.io/badge/dependencies-none-0e9f6e?style=flat-square)

</div>

---

```bash
uremote descubrir                 # find the TVs on your network and say what they are
uremote mandar vol+ ch+ ok        # send keys in a chain
uremote app netflix               # open apps (deep-linking to titles on Roku)
uremote gui                       # the graphical remote
```

## What it is

A **command-line tool** and a **graphical remote**, the same program either way.
It speaks each brand's own network protocol directly — no vendor cloud, no
account, no phone app in the middle, and nothing leaves your LAN.

The design idea is that **a TV is a profile, not a special case**. Adding a
television means writing one JSON file with its keys and its button layout. Only
if the protocol itself is new do you write code, and that's about fifty lines.

## Purpose and scope

**The purpose.** To stop losing the remote. Also to make a television something a
script can drive: if `uremote mandar power` is a command, then turning the TV off
at midnight is a cron job rather than a discipline.

**What it covers.** Discovery, keys, text entry, apps, recordable macros, per-TV
state files, a scheduler with pluggable conditions, offline voice control, and a
hunter that goes and finds your TV's PDF manual.

**What it does not do.** No cloud, no remote access from outside your network, no
account. If you're not on the same WiFi, it can't help you — that's the trade for
having no dependency on anyone's server.

## Contents

- [What it is](#what-it-is) · [Purpose and scope](#purpose-and-scope)
- [Install](#install) · [Supported protocols](#supported-protocols)
- [How to start (CLI)](#how-to-start-cli)
- [The scheduler](#the-scheduler) · [Voice control](#voice-control)
- [The graphical remote](#the-graphical-remote)
- [Adding a new brand](#adding-a-new-brand)
- [For developers](#contributing)

## Install

**pip** — leaves `uremote` and `manualhunt` available in cmd and PowerShell:

```bash
pip install git+https://github.com/leostriker111/URemote
```

**Portable script** — clones to `~\URemote` and adds it to your user `PATH`:

```powershell
irm https://raw.githubusercontent.com/leostriker111/URemote/main/get-uremote.ps1 | iex
```

**Installer** — grab `uremote-setup.exe` from [Releases](../../releases).

## Supported protocols

| brand | protocol | status |
|---|---|---|
| **Panasonic Viera** (2011-2017) | SOAP/UPnP `:55000` | ✅ Tested. No pairing; reads real volume and mute |
| **Roku / Roku TV** | ECP `:8060` | ✅ Tested. Deep-linked apps, text entry, active app |
| **Android TV / Google TV** | adb `:5555` | ✅ Tested. Needs network debugging turned on |
| **LG webOS** | webOS websocket | ⚠️ Driver written, **never tested against a set** |
| **Samsung Tizen** | Tizen websocket | ⚠️ Driver written, **never tested against a set** |

The two untested ones are exactly where a contribution would help most — see
[Contributing](#contributing).

## How to start (CLI)

### Finding and registering a TV

```bash
uremote descubrir                                    # what's on the network?
uremote tvs agregar sala 192.168.1.185 panasonic_viera
uremote teclas                                       # which buttons this profile has
```

Discovery is SSDP/UPnP: it finds the sets, pulls their real name and model, and in
the GUI you link them with a click.

### Driving it

| command | what it does |
|---|---|
| `uremote mandar power` | Any button in the profile. Chains: `mandar vol+ vol+ ok`. |
| `uremote texto hola` | Types into the TV (Roku and Android). |
| `uremote app youtube --tv sala` | Opens an app; on Roku it can deep-link to a title. |
| `uremote estado leer --vivo` | The state file: last key, last input, real volume where the protocol gives it. |
| `uremote estado set perfil_imagen cine` | Free-form fields you define yourself. |
| `uremote manual --abrir` | **Finds your TV's manual.** Searches for the PDF, validates it's the right one, downloads it — and if the brand no longer publishes a PDF, opens their official portal instead. |
| `uremote selftest` | Checks you haven't broken the engine. |

### Macros

```bash
uremote macro grabar noche     # start recording
...                            # press buttons
uremote macro fin              # stop
uremote macro correr noche     # replay it
```

What you get is an editable `.txt`, not an opaque blob — `espera N` between steps
is just a line you can add by hand.

## The scheduler

Commands that fire when conditions are met, chained with AND:

```bash
uremote agenda instalar        # registers a Windows scheduled task that ticks every minute
```

Entries live in `config/agenda.json`. Each one carries a list of **conditions**,
and conditions are plug-ins — one file each, in `uremote/condiciones/`:

| condition | fires when |
|---|---|
| `hora` | a given time of day |
| `arranque` | the computer starts |
| `tv_encendida` | the TV is actually on |

Each condition returns a **stamp** identifying *this* occurrence, and the agenda
fires once per stamp. That is what stops a minute-by-minute tick from running your
"turn everything off" entry sixty times in an hour.

Writing a new condition means one file exposing `AYUDA` and
`se_cumple(params, entrada)`. Nothing else has to know it exists.

## Voice control

Windows, and **entirely offline**:

```bash
uremote voz escuchar           # say "ya estuvo" to stop
```

The microphone listens for "sube volumen", "canal arriba" and the rest. The
grammar is closed and in Spanish on purpose: a fixed vocabulary is what makes
recognition reliable without a model in the cloud.

It also reads out loud:

```bash
uremote voz leer notas.txt          # speak the file
uremote voz leer guion.txt --wav    # write a .wav instead, silently
uremote voz leer guion.txt --oir    # save it and play it
```

## The graphical remote

```bash
uremote gui
```

The buttons are generated from the TV's profile, so a Viera and a Roku give you
different remotes and neither shows a key that would do nothing.

The detail worth knowing: **the built-in console prints the equivalent CLI
command for every button you press.** The graphical remote teaches you the
terminal one.

## Adding a new brand

1. Copy a profile from `uremote/profiles/` and adjust the keys and layout.
2. If it uses a protocol that already exists (ECP, Viera SOAP, adb), you're done.
3. If not, write `uremote/drivers/mybrand.py` with a `Driver(Base)` class that
   implements `mandar(codigo)` — and catch the usual connection error with a
   message saying which menu to enable on the TV.
4. Run `uremote selftest`.

Step 3's parenthesis is not decoration. Every one of these protocols refuses
connections until you turn something on in a settings menu nobody can find, and
**a good error message is most of what makes this usable.**

<br>

---

<div align="center">

## 🔧 For developers

*Everything above is what it does. Everything below is how it does it.*

</div>

---

### Contributing

The most valuable contributions, in order:

1. **Test the LG webOS and Samsung Tizen drivers.** They're written and have never
   met a real television. If you own one, `uremote descubrir` followed by a single
   `uremote mandar power` already tells us something worth knowing.
2. **New brands.** Vizio, Hisense, Chromecast. Mostly one JSON file each.
3. **Voice control on Linux and macOS** — the engine in `voz/motor.py` is the only
   Windows-specific part of the project.

### What it's made of

**Python 3.8+ with no external dependencies.** Every protocol here is HTTP,
SOAP, SSDP or a websocket, and all of those are reachable from the standard
library. Staying dependency-free is what lets it ship as a portable folder you
can drop on any machine.

### The modules

| area | modules | what's there |
|---|---|---|
| **drivers** | `panasonic_viera.py` 38 · `roku.py` 54 · `androidtv.py` 54 · `lg_webos.py` 86 · `samsung_tizen.py` 60 · `base.py` 24 · `dummy.py` 10 | One file per protocol, all behind `Base.mandar(codigo)`. The line counts are the argument for the profile design: a whole brand is under sixty lines. |
| **core** | `agenda.py` 150 · `notifica.py` 79 · `control.py` 74 · `devices.py` 48 · `intents.py` 43 · `state.py` 40 · `macros.py` 38 · `guion.py` 29 · `registry.py` 24 · `paths.py` 16 | The engine: the scheduler, the registry of known TVs, state files, macros. |
| **conditions** | `hora.py` 17 · `tv_encendida.py` 22 · `arranque.py` 10 · `__init__.py` 18 | The plug-in conditions, loaded by name with `importlib`. |
| **interfaces** | `cli.py` 292 · `gui/app.py` 416 · `discover.py` 69 · `theme.py` 22 | The two faces, plus SSDP discovery. |
| **voice** | `voz/motor.py` 88 · `voz/__main__.py` 61 · `voz/comandos.py` 32 | Recognition and TTS, Windows only. |
| **manuals** | `manualhunt/hunt.py` 119 | Finding and validating the PDF. |

### The decision that shaped it

The obvious way to write this is a class per television with a method per button.
That is also how it becomes unmaintainable at the third brand, because 90 % of
those classes are the same and the 10 % that differs is buried.

So the split is: **a profile is data and a driver is transport.** A profile is a
JSON file listing which keys exist and how to lay them out. A driver only knows
how to put one code on the wire. The GUI reads the profile to decide what to draw,
which is why it never shows a button the set can't do; and adding a TV that speaks
an existing protocol touches no Python at all.

The conditions in the scheduler follow the same shape for the same reason — one
file, one job, discovered by name.

### License

[MIT](LICENSE) — [Leostriker](https://github.com/leostriker111).

### Related projects

- **[Home Assistant](https://www.home-assistant.io/)** — *use that if you want a
  whole smart home;* URemote is one command for televisions, and it will still be
  one file you can read.
- **`adb`** — what the Android TV driver is standing on. If your TV is Android and
  you already know adb, you may not need this.
