"""Schnittstelle für Datenquellen.

Kernidee der Architektur: Der Rest des Programms weiß NICHT, woher Inserate
kommen. Jede Quelle (Demo-Daten, E-Mail-Postfach, API, ...) erbt von
`ListingSource` und liefert `CarListing`-Objekte. Neue Quelle = neue Klasse,
sonst ändert sich nichts. Das nennt man "Programmieren gegen Schnittstellen".
"""

from abc import ABC, abstractmethod

from carhunt.models import CarListing


class ListingSource(ABC):
    """Basisklasse: Jede Datenquelle liefert Inserate im selben Format."""

    name: str = "unbenannt"

    @abstractmethod
    def fetch(self) -> list[CarListing]:
        """Holt die aktuellen Inserate dieser Quelle."""
