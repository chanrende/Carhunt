"""Datenmodelle: die "Sprache", in der alle Teile des Programms miteinander reden.

Egal woher ein Inserat kommt (Demo-Daten, E-Mail-Parser, API) – jede Quelle
übersetzt es in ein `CarListing`. Der Rest des Programms kennt nur dieses Format.
"""

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseType(StrEnum):
    """Wie das Fahrzeug erworben wird."""

    KAUF = "kauf"
    FINANZIERUNG = "finanzierung"
    LEASING = "leasing"


class CarListing(BaseModel):
    """Ein einzelnes Fahrzeug-Inserat."""

    id: str
    title: str
    brand: str
    model: str
    price_eur: int = Field(ge=0, description="Kaufpreis in Euro")
    mileage_km: int | None = None
    first_registration_year: int | None = None
    purchase_type: PurchaseType = PurchaseType.KAUF
    url: str
    source: str
    description: str | None = None


# Übung 5: erweitere die erlaubten Operatoren um "contains" (Textsuche).
Operator = Literal["==", "!=", "<", "<=", ">", ">="]


class FilterRule(BaseModel):
    """Eine frei konfigurierbare Ad-hoc-Regel: <Attribut> <Operator> <Wert>.

    Beispiel in der YAML-Config:
        custom_filters:
          - attribute: first_registration_year
            operator: ">="
            value: 2006
    """

    attribute: str
    operator: Operator
    value: Any

    @field_validator("attribute")
    @classmethod
    def attribute_must_exist_on_listing(cls, v: str) -> str:
        """Fail fast: Tippfehler fliegen beim Laden der Config auf, nicht zur Laufzeit."""
        if v not in CarListing.model_fields:
            valid = ", ".join(CarListing.model_fields)
            raise ValueError(f"Unbekanntes Attribut '{v}'. Verfügbar: {valid}")
        return v


class SearchProfile(BaseModel):
    """Deine Suchkriterien – wird aus config/search_profile.yaml geladen."""

    max_price_eur: int = Field(gt=0)
    brands: list[str]
    excluded_purchase_types: list[PurchaseType] = [PurchaseType.LEASING]
    max_mileage_km: int | None = None
    min_year: int | None = None
    custom_filters: list[FilterRule] = []
    capital_eur: int | None = Field(default=None, description="Nur Info, keine Filterwirkung")
