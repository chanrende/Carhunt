"""Tests für die Persistenz (Übung 3, Phase 2).

Das ist Test-Driven Development: Die Tests beschreiben das Zielverhalten,
BEVOR der Code existiert. Entferne die pytestmark-Zeile und implementiere
src/carhunt/storage.py, bis alles grün ist.

`tmp_path` ist eine pytest-Fixture: ein frischer Temp-Ordner pro Test,
damit Tests sich nie gegenseitig beeinflussen.
"""

import pytest

from carhunt.models import CarListing
from carhunt.storage import ListingRepository

pytestmark = pytest.mark.skip(reason="Übung 3: Diese Zeile entfernen und storage.py implementieren")


def make_listing(listing_id: str) -> CarListing:
    return CarListing(
        id=listing_id,
        title="Testwagen",
        brand="Toyota",
        model="Yaris",
        price_eur=2500,
        url=f"https://example.com/{listing_id}",
        source="test",
    )


def test_new_listings_are_returned(tmp_path):
    repo = ListingRepository(tmp_path / "test.sqlite3")
    new = repo.save_new([make_listing("a"), make_listing("b")])
    assert {listing.id for listing in new} == {"a", "b"}


def test_known_listings_are_not_returned_again(tmp_path):
    repo = ListingRepository(tmp_path / "test.sqlite3")
    repo.save_new([make_listing("a")])
    new = repo.save_new([make_listing("a"), make_listing("b")])
    assert [listing.id for listing in new] == ["b"]


def test_count(tmp_path):
    repo = ListingRepository(tmp_path / "test.sqlite3")
    repo.save_new([make_listing("a"), make_listing("b")])
    repo.save_new([make_listing("b"), make_listing("c")])
    assert repo.count() == 3
