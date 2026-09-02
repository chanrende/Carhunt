"""Demo-Quelle mit Beispieldaten.

Damit entwickelst und testest du die komplette Pipeline, ohne von echten
Portalen abhängig zu sein. In Phase 5 kommt eine echte Quelle dazu –
mit exakt derselben Schnittstelle.
"""

import json
from pathlib import Path

from carhunt.models import CarListing
from carhunt.sources.base import ListingSource


class MockSource(ListingSource):
    """Liest Inserate aus einer JSON-Datei neben diesem Modul."""

    name = "mock"

    def __init__(self, data_file: Path | None = None) -> None:
        self._data_file = data_file or Path(__file__).with_name("sample_listings.json")

    def fetch(self) -> list[CarListing]:
        raw = json.loads(self._data_file.read_text(encoding="utf-8"))
        return [CarListing(**item) for item in raw]
