"""Filterlogik: Welche Inserate passen zum Suchprofil?

Bewusst reine Funktionen ohne Netzwerk oder Datenbank –
dadurch extrem leicht zu testen (siehe tests/test_filters.py).
"""

import operator as op
from collections.abc import Callable
from typing import Any

from carhunt.models import CarListing, FilterRule, SearchProfile

# Zuordnung Operator-Text -> echte Vergleichsfunktion aus der Standardbibliothek.
_OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "==": op.eq,
    "!=": op.ne,
    "<": op.lt,
    "<=": op.le,
    ">": op.gt,
    ">=": op.ge,
    # Übung 5: "contains" für Textsuche ergänzen (Test wartet in test_filters.py).
}


def matches_rule(listing: CarListing, rule: FilterRule) -> bool:
    """Wendet eine einzelne Ad-hoc-Regel auf ein Inserat an.

    Der Trick dahinter: getattr() liest ein Attribut über seinen NAMEN als
    Text aus. Dadurch kann die Config über Felder filtern, die diese Funktion
    gar nicht kennt – neue Kriterien brauchen keine Codeänderung mehr.
    """
    actual = getattr(listing, rule.attribute)
    if actual is None:
        # Bewusste Entscheidung: fehlende Angaben schließen ein Inserat nicht aus.
        return True
    try:
        return _OPERATORS[rule.operator](actual, rule.value)
    except TypeError as exc:
        raise ValueError(
            f"Regel '{rule.attribute} {rule.operator} {rule.value!r}' passt nicht zum "
            f"Datentyp des Attributs (Wert im Inserat: {actual!r})."
        ) from exc


def normalize_brand(brand: str) -> str:
    """Vereinheitlicht Markennamen für den Vergleich, z. B. "  VW " -> "vw".

    Übung 1: Inserate schreiben statt "VW" oft "Volkswagen" aus – solche
    Treffer gehen uns aktuell verloren. Erweitere diese Funktion um ein
    Alias-Mapping (z. B. "volkswagen" -> "vw"), sodass beide Schreibweisen
    auf denselben Wert normalisiert werden.
    Der Test dafür wartet in tests/test_filters.py (Skip-Marker entfernen).
    """
    return brand.strip().lower()


def matches(listing: CarListing, profile: SearchProfile) -> bool:
    """True, wenn das Inserat alle Kriterien des Profils erfüllt."""
    if listing.price_eur > profile.max_price_eur:
        return False

    if listing.purchase_type in profile.excluded_purchase_types:
        return False

    allowed_brands = {normalize_brand(b) for b in profile.brands}
    if normalize_brand(listing.brand) not in allowed_brands:
        return False

    if (
        profile.max_mileage_km is not None
        and listing.mileage_km is not None
        and listing.mileage_km > profile.max_mileage_km
    ):
        return False

    # Ad-hoc-Regeln aus der Config: ALLE müssen zutreffen.
    for rule in profile.custom_filters:
        if not matches_rule(listing, rule):
            return False

    # Übung 2: Filtere zusätzlich nach profile.min_year (Erstzulassung).
    # Denk an den Fall, dass min_year oder first_registration_year None sein kann.

    return True


def filter_listings(listings: list[CarListing], profile: SearchProfile) -> list[CarListing]:
    """Behält nur die Inserate, die zum Profil passen."""
    return [listing for listing in listings if matches(listing, profile)]
