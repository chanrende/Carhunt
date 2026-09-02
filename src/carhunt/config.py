"""Lädt das Suchprofil aus einer YAML-Datei und validiert es über Pydantic."""

from pathlib import Path

import yaml

from carhunt.models import SearchProfile


def load_profile(path: str | Path) -> SearchProfile:
    """Liest die YAML-Datei ein; Pydantic prüft Typen und Pflichtfelder."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    # Schlüssel ohne Wert (z. B. auskommentierte Regel-Listen) -> Modell-Default nutzen.
    data = {key: value for key, value in data.items() if value is not None}
    return SearchProfile(**data)
