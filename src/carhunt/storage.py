"""Persistenz: bekannte Inserate merken, damit wir nur NEUE melden.

Das ist das Herzstück eines Such-Agenten, der regelmäßig läuft: Ohne Gedächtnis
würde er dir jeden Tag dieselben Autos melden.

Übung 3 (Phase 2): Implementiere `ListingRepository` mit SQLite.
- Modul `sqlite3` ist in Python eingebaut, keine Installation nötig.
- Vorschlag für die Tabelle:
    CREATE TABLE IF NOT EXISTS listings (
        id TEXT PRIMARY KEY,
        first_seen TEXT NOT NULL,
        data TEXT NOT NULL   -- das ganze Inserat als JSON (listing.model_dump_json())
    )
- Die Tests in tests/test_storage.py beschreiben das erwartete Verhalten.
  Entferne dort den Skip-Marker und arbeite dich Test für Test grün.
"""

import sqlite3  # noqa: F401  (brauchst du in Übung 3)
from pathlib import Path

from carhunt.models import CarListing


class ListingRepository:
    """Speichert Inserate in einer SQLite-Datei und erkennt Duplikate."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        # TODO (Übung 3): Verbindung öffnen und Tabelle anlegen.

    def save_new(self, listings: list[CarListing]) -> list[CarListing]:
        """Speichert Inserate und gibt nur die zurück, die vorher unbekannt waren."""
        raise NotImplementedError("Übung 3: siehe tests/test_storage.py")

    def count(self) -> int:
        """Anzahl aller gespeicherten Inserate."""
        raise NotImplementedError("Übung 3: siehe tests/test_storage.py")
