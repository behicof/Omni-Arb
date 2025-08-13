"""Lightweight JSON storage utilities."""
from pathlib import Path
from typing import Any
import json


def save(path: str | Path, data: Any) -> None:
    """Persist data as JSON to *path*."""
    Path(path).write_text(json.dumps(data))


def load(path: str | Path) -> Any:
    """Load JSON data from *path*."""
    return json.loads(Path(path).read_text())
