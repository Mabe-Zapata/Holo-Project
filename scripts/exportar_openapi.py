"""Genera odds/openapi.json a partir de la aplicación.

Uso (desde la raíz del repositorio):
    python scripts/exportar_openapi.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.main import app  # noqa: E402

destino = RAIZ / "odds" / "openapi.json"
destino.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Especificación escrita en {destino.relative_to(RAIZ)}")
