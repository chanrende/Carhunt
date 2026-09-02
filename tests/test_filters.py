"""Tests für die Filterlogik.

So liest du einen Test: "Gegeben diese Daten, erwarte ich dieses Ergebnis."
Tests sind dein Sicherheitsnetz – wenn du später etwas umbaust und alle
Tests grün bleiben, hast du sehr wahrscheinlich nichts kaputt gemacht.
"""

import pytest
from pydantic import ValidationError

from carhunt.filters import filter_listings, matches, matches_rule
from carhunt.models import CarListing, FilterRule, PurchaseType, SearchProfile


def make_listing(**overrides) -> CarListing:
    """Testhelfer: baut ein gültiges Inserat, einzelne Felder überschreibbar."""
    base = {
        "id": "t-1",
        "title": "Testwagen",
        "brand": "Toyota",
        "model": "Yaris",
        "price_eur": 2500,
        "mileage_km": 120000,
        "first_registration_year": 2009,
        "purchase_type": PurchaseType.KAUF,
        "url": "https://example.com/t-1",
        "source": "test",
    }
    base.update(overrides)
    return CarListing(**base)


def make_profile(**overrides) -> SearchProfile:
    base = {
        "max_price_eur": 3000,
        "brands": ["Toyota", "VW"],
        "excluded_purchase_types": [PurchaseType.LEASING],
    }
    base.update(overrides)
    return SearchProfile(**base)


def test_price_exactly_at_limit_passes():
    assert matches(make_listing(price_eur=3000), make_profile()) is True


def test_price_above_limit_fails():
    assert matches(make_listing(price_eur=3001), make_profile()) is False


def test_wrong_brand_fails():
    assert matches(make_listing(brand="BMW"), make_profile()) is False


def test_brand_comparison_ignores_case_and_spaces():
    assert matches(make_listing(brand="  toyota "), make_profile()) is True


def test_leasing_is_excluded():
    listing = make_listing(purchase_type=PurchaseType.LEASING)
    assert matches(listing, make_profile()) is False


def test_mileage_above_limit_fails():
    profile = make_profile(max_mileage_km=100000)
    assert matches(make_listing(mileage_km=100001), profile) is False


def test_filter_listings_keeps_only_matches():
    listings = [
        make_listing(id="ok"),
        make_listing(id="too_expensive", price_eur=9999),
    ]
    result = filter_listings(listings, make_profile())
    assert [listing.id for listing in result] == ["ok"]


# --- Ad-hoc-Filter (Regel-Engine) --------------------------------------------


def test_custom_rule_filters_by_year():
    profile = make_profile(
        custom_filters=[FilterRule(attribute="first_registration_year", operator=">=", value=2006)]
    )
    assert matches(make_listing(first_registration_year=2004), profile) is False
    assert matches(make_listing(first_registration_year=2006), profile) is True


def test_custom_rule_missing_value_does_not_exclude():
    rule = FilterRule(attribute="mileage_km", operator="<=", value=100000)
    assert matches_rule(make_listing(mileage_km=None), rule) is True


def test_multiple_custom_rules_must_all_match():
    profile = make_profile(
        custom_filters=[
            FilterRule(attribute="price_eur", operator="<=", value=2600),
            FilterRule(attribute="mileage_km", operator="<=", value=110000),
        ]
    )
    assert matches(make_listing(price_eur=2500, mileage_km=120000), profile) is False
    assert matches(make_listing(price_eur=2500, mileage_km=100000), profile) is True


def test_unknown_attribute_is_rejected_when_rule_is_created():
    with pytest.raises(ValidationError):
        FilterRule(attribute="farbe", operator="==", value="rot")


@pytest.mark.skip(reason="Übung 5: 'contains' in models.py (Operator) UND filters.py ergänzen")
def test_contains_operator_searches_text():
    """Textsuche, z. B. 'Klima' in der Beschreibung.

    Achtung, Feinheit: Bei description=None soll 'contains' False liefern –
    unbekannter Text ist kein Treffer. Überlege, warum das hier anders ist
    als bei den Zahlenvergleichen.
    """
    rule = FilterRule(attribute="description", operator="contains", value="Klima")
    assert matches_rule(make_listing(description="Klimaanlage, Alufelgen"), rule) is True
    assert matches_rule(make_listing(description="8-fach bereift"), rule) is False
    assert matches_rule(make_listing(description=None), rule) is False


@pytest.mark.skip(reason="Übung 1: Alias-Mapping in normalize_brand() bauen, dann Skip entfernen")
def test_volkswagen_alias_matches_vw():
    """'Volkswagen' im Inserat soll auf 'VW' im Profil passen."""
    assert matches(make_listing(brand="Volkswagen"), make_profile()) is True


@pytest.mark.skip(reason="Übung 2: min_year-Filter in matches() bauen, dann Skip entfernen")
def test_min_year_filters_old_cars():
    profile = make_profile(min_year=2006)
    assert matches(make_listing(first_registration_year=2004), profile) is False
    assert matches(make_listing(first_registration_year=2006), profile) is True
