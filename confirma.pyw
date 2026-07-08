"""Handler del protocolo uremote:// — lo lanza Windows al picar un toast."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from uremote.core import notifica

if len(sys.argv) > 1:
    notifica.responder(sys.argv[1])
