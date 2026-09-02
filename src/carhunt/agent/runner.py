"""Ein minimaler KI-Agent (Phase 4).

So funktioniert der Agent-Loop – das Grundmuster fast aller KI-Agenten:

1. Wir schicken Claude eine Aufgabe + eine Liste unserer Tools.
2. Antwortet Claude mit einem Tool-Aufruf ("tool_use"), führen WIR das Tool
   lokal aus und schicken das Ergebnis ("tool_result") zurück.
3. Das wiederholt sich, bis Claude keine Tools mehr braucht und eine
   finale Textantwort gibt.

Das Modell hat also keinen Zugriff auf deinen Rechner – es *bittet* dein
Programm, Funktionen auszuführen. Du behältst die Kontrolle.

Voraussetzung: Umgebungsvariable ANTHROPIC_API_KEY
  Windows (PowerShell):  $env:ANTHROPIC_API_KEY = "sk-ant-..."
  Linux/Mac:             export ANTHROPIC_API_KEY="sk-ant-..."

Übung 4: Gib dem Agenten ein zweites Tool `get_search_profile`, das das
Suchprofil als JSON liefert – dann kann er seine Empfehlung explizit an
deinen Kriterien ausrichten.
"""

import json
from pathlib import Path

import anthropic

from carhunt.config import load_profile
from carhunt.filters import filter_listings
from carhunt.sources.mock_source import MockSource

# Aktuelle Modell-IDs: https://docs.claude.com/en/docs/about-claude/models/overview
MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = (
    "Du bist ein nüchterner, ehrlicher Berater für den Gebrauchtwagenkauf. "
    "Hole dir die aktuellen Treffer über das bereitgestellte Tool. "
    "Bewerte sie nach Preis-Leistung (Preis, Laufleistung, Baujahr, bekannte "
    "Stärken und Schwächen des Modells). Empfiehl die besten drei mit kurzer "
    "Begründung und nenne pro Fahrzeug 2-3 Punkte, die man bei der "
    "Besichtigung unbedingt prüfen sollte. Antworte auf Deutsch und kompakt."
)

TOOLS = [
    {
        "name": "get_matching_listings",
        "description": (
            "Liefert alle Fahrzeug-Inserate, die zum Suchprofil des Nutzers "
            "passen, als JSON-Liste."
        ),
        "input_schema": {"type": "object", "properties": {}},
    }
]


def _run_tool(tool_name: str, tool_input: dict, config_path: Path) -> str:
    """Führt einen vom Modell angeforderten Tool-Aufruf lokal aus."""
    if tool_name == "get_matching_listings":
        profile = load_profile(config_path)
        hits = filter_listings(MockSource().fetch(), profile)
        return json.dumps([h.model_dump(mode="json") for h in hits], ensure_ascii=False)
    return f"Unbekanntes Tool: {tool_name}"


def run_agent(task: str, config_path: str | Path) -> str:
    """Führt den Agent-Loop aus und gibt die finale Textantwort zurück."""
    client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
    config_path = Path(config_path)
    messages: list[dict] = [{"role": "user", "content": task}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Fertig? Dann alle Textblöcke der Antwort zusammensetzen.
        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        # Claude will ein oder mehrere Tools nutzen:
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"[Agent ruft Tool auf: {block.name}]")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _run_tool(block.name, block.input, config_path),
                    }
                )
        messages.append({"role": "user", "content": tool_results})
