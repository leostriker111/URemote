"""Lanzador del tick para la tarea de Windows (sin ventana)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uremote.core import agenda

agenda.tick()
