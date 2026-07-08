"""Puente a System.Speech de Windows vía powershell 5.1 (.NET Framework,
siempre trae reconocimiento y síntesis; PS7 no carga System.Speech).
Sin dependencias de Python."""

import subprocess
import tempfile
from pathlib import Path

PS = ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]


def _ps(texto: str) -> str:
    """Literal PowerShell entre comillas simples."""
    return "'" + texto.replace("'", "''") + "'"


def voces() -> list:
    script = ("Add-Type -AssemblyName System.Speech; "
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              "$s.GetInstalledVoices() | ForEach-Object "
              "{ $_.VoiceInfo.Name + ' | ' + $_.VoiceInfo.Culture.Name }")
    r = subprocess.run(PS + ["-Command", script], capture_output=True,
                       text=True, timeout=30)
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def leer(archivo: Path, voz: str = "", wav: str = "", velocidad: int = 0,
         volumen: int = 100, oir: bool = False):
    """Lee un txt con TTS. Con `wav` lo genera en silencio (no suena);
    sin `wav` lo habla por las bocinas; wav + oir hace las dos."""
    partes = ["Add-Type -AssemblyName System.Speech;",
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"]
    if voz:
        partes.append(f"$s.SelectVoice({_ps(voz)});")
    if wav:
        partes.append(f"$s.SetOutputToWaveFile({_ps(str(wav))});")
    partes.append(f"$s.Rate = {int(velocidad)};")
    partes.append(f"$s.Volume = {max(0, min(100, int(volumen)))};")
    partes.append(f"$texto = [IO.File]::ReadAllText({_ps(str(archivo))}, "
                  "[Text.Encoding]::UTF8);")
    partes.append("$s.Speak($texto); $s.Dispose();")
    if wav and oir:
        partes.append(f"(New-Object System.Media.SoundPlayer {_ps(str(wav))}).PlaySync();")
    r = subprocess.run(PS + ["-Command", " ".join(partes)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"TTS falló: {r.stderr.strip()[:200]}")


def escuchar(frases: list, al_reconocer, eco=print, confianza: float = 0.5):
    """Escucha el micrófono con una gramática cerrada de `frases` y llama
    `al_reconocer(frase)` por cada una. Bloquea hasta Ctrl+C o que
    `al_reconocer` regrese False."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8-sig") as f:
        f.write("\n".join(frases))
        archivo_frases = f.name
    script = f"""
Add-Type -AssemblyName System.Speech
$rec = $null
foreach ($c in @('es-MX','es-ES','es-419')) {{
  try {{ $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine([System.Globalization.CultureInfo]$c); break }} catch {{}}
}}
if (-not $rec) {{ try {{ $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine }} catch {{ Write-Output '!!error: no hay reconocedor de voz instalado en Windows'; exit 1 }} }}
$frases = Get-Content -Encoding UTF8 {_ps(archivo_frases)}
$choices = New-Object System.Speech.Recognition.Choices
foreach ($f in $frases) {{ if ($f.Trim()) {{ $choices.Add($f.Trim()) }} }}
$gb = New-Object System.Speech.Recognition.GrammarBuilder
$gb.Culture = $rec.RecognizerInfo.Culture
$gb.Append($choices)
$rec.LoadGrammar((New-Object System.Speech.Recognition.Grammar($gb)))
try {{ $rec.SetInputToDefaultAudioDevice() }} catch {{ Write-Output '!!error: no hay micrófono'; exit 1 }}
Write-Output ('!!escuchando (' + $rec.RecognizerInfo.Culture.Name + ')')
while ($true) {{
  $r = $rec.Recognize([TimeSpan]::FromSeconds(4))
  if ($r -and $r.Confidence -gt {float(confianza)}) {{ Write-Output $r.Text }}
}}
"""
    proc = subprocess.Popen(PS + ["-Command", script], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True,
                            encoding="utf-8", errors="replace", bufsize=1)
    try:
        for linea in proc.stdout:
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith("!!"):
                eco(linea[2:])
                if "error" in linea:
                    return
                continue
            if al_reconocer(linea) is False:
                break
    except KeyboardInterrupt:
        pass
    finally:
        proc.kill()
        Path(archivo_frases).unlink(missing_ok=True)
