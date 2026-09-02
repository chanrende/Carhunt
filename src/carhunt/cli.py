"""Kommandozeilen-Interface.

    carhunt search   -> Suchlauf: Quelle abfragen, filtern, Treffer anzeigen
    carhunt agent    -> KI-Agent bewertet die Treffer (braucht ANTHROPIC_API_KEY)
"""

import argparse

from carhunt.config import load_profile
from carhunt.filters import filter_listings
from carhunt.sources.mock_source import MockSource


def cmd_search(args: argparse.Namespace) -> None:
    profile = load_profile(args.config)
    source = MockSource()
    listings = source.fetch()
    hits = filter_listings(listings, profile)

    print(f"\nQuelle '{source.name}': {len(hits)} von {len(listings)} Inseraten passen:\n")
    for hit in sorted(hits, key=lambda x: x.price_eur):
        km = f"{hit.mileage_km} km" if hit.mileage_km is not None else "km k. A."
        year = hit.first_registration_year or "Jahr k. A."
        print(f"  {hit.price_eur:>5} €  {hit.brand} {hit.model}  ({year}, {km})")
        print(f"          {hit.url}")
    print()


def cmd_agent(args: argparse.Namespace) -> None:
    # Import erst hier, damit "carhunt search" auch ohne API-Key funktioniert.
    from carhunt.agent.runner import run_agent

    answer = run_agent(
        task="Bewerte die aktuellen Treffer und empfiehl mir die besten drei.",
        config_path=args.config,
    )
    print(f"\n{answer}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="carhunt",
        description="Agentengestützte Gebrauchtwagen-Suche (Lernprojekt)",
    )
    parser.add_argument(
        "--config",
        default="config/search_profile.yaml",
        help="Pfad zum Suchprofil (Standard: config/search_profile.yaml)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_search = subparsers.add_parser("search", help="Suchlauf mit der aktuellen Quelle")
    p_search.set_defaults(func=cmd_search)

    p_agent = subparsers.add_parser("agent", help="KI-Agent bewertet die Treffer")
    p_agent.set_defaults(func=cmd_agent)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
