# shared/utils.py
"""
Utility helpers that are used by both the desktop and the web app.
"""

import json
from pathlib import Path
from typing import Any, Dict
import sys

def resource_path(relative_path: str) -> str:
    """
    Works for normal runs and for PyInstaller bundles.
    """
    try:
        # PyInstaller creates a temporary folder stored in _MEIPASS
        base_path = Path(sys._MEIPASS)  # type: ignore
    except Exception:
        base_path = Path(__file__).parent.parent  # project root
    return str(base_path / relative_path)

def load_json(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and return a dict."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Write a dict to a JSON file (pretty‑printed)."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
