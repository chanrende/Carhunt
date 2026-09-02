"""Prüft, dass die echte Konfigurationsdatei lädt und deine Kriterien enthält."""

from pathlib import Path

from carhunt.config import load_profile
from carhunt.models import PurchaseType

CONFIG_FILE = Path(__file__).parents[1] / "config" / "search_profile.yaml"


def test_default_profile_loads():
    profile = load_profile(CONFIG_FILE)
    assert profile.max_price_eur == 3000
    assert "VW" in profile.brands
    assert len(profile.brands) == 7
    assert PurchaseType.LEASING in profile.excluded_purchase_types
