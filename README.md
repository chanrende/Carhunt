# carhunt – dein Auto-Such-Agent (Lernprojekt)

Ein Programm, das Gebrauchtwagen-Inserate gegen dein Suchprofil prüft
(max. 3.000 €, deine 7 Marken, kein Leasing) und dir am Ende von einem
KI-Agenten bewerten lässt, welche Treffer sich lohnen.

Gleichzeitig ist es dein Lehrpfad: Das Projekt ist aufgebaut wie ein echtes
professionelles Python-Repository, und du baust es Phase für Phase aus.
Übungen stecken direkt im Code – suche nach dem Wort **"Übung"**.

---

## Schnellstart (Phase 0)

Voraussetzungen: [Python](https://www.python.org/downloads/) 3.11 bis 3.14
(deine Version 3.14 wird unterstützt; bei der Windows-Installation „Add
python.exe to PATH" anhaken), [Git](https://git-scm.com/), als Editor
empfohlen: VS Code.

Im Projektordner ein Terminal öffnen, dann:

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
carhunt search
```

**Linux / Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
carhunt search
```

**Fertig, wenn:** `pytest` grün ist (einige Tests werden übersprungen – das
sind deine Übungen, so soll es sein) und `carhunt search` **6 Treffer** aus
den Demo-Daten anzeigt.

Danach direkt die erste Berufspraxis: Projekt unter Versionskontrolle stellen.

```bash
git init
git add .
git commit -m "Initial commit: Projektgerüst"
```

Ab jetzt gilt: **nach jedem abgeschlossenen Schritt ein Commit** mit einer
kurzen Nachricht, die sagt, *was* du geändert hast.

---

## Python-Versionen sicher verwalten (Plan B)

Deine Python 3.14 funktioniert: Alle Abhängigkeiten sind offiziell dafür
freigegeben, und die Mindestversionen in `pyproject.toml` schreiben genau das
fest (pydantic ≥ 2.12, PyYAML ≥ 6.0.3, pytest ≥ 8.4 – die Kommentare dort
erklären warum). Die komplette Testsuite läuft unter 3.14 grün.

Falls du je eine andere Version brauchst – z. B. weil eine Bibliothek das
allerneueste Python noch nicht unterstützt – gilt eine eiserne Profi-Regel:
**Die vorhandene Python-Installation wird niemals überschrieben oder
deinstalliert.** Stattdessen liegen Versionen nebeneinander, und die venv des
Projekts entscheidet, welche gilt. Das Standardwerkzeug dafür ist
[uv](https://docs.astral.sh/uv/):

**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux / Mac**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Danach holst du z. B. Python 3.12 zusätzlich und legst das Projekt-venv damit
neu an (altes `.venv` vorher löschen, Terminal danach neu öffnen):

```bash
uv python install 3.12
uv venv --seed --python 3.12 .venv
```

Ab hier läuft alles wie gewohnt: venv aktivieren, `pip install -e ".[dev]"`,
`pytest`. Zurück auf die neueste Version? Gleiches Spiel mit `--python 3.14`.

---

## Wie das Projekt aufgebaut ist

```
carhunt/
├── config/search_profile.yaml   # DEINE Kriterien – Daten getrennt vom Code
├── src/carhunt/
│   ├── models.py                # Datenmodelle (Pydantic) – die gemeinsame Sprache
│   ├── config.py                # lädt + validiert das Suchprofil
│   ├── filters.py               # Filterlogik (reine Funktionen, gut testbar)
│   ├── storage.py               # Gedächtnis: nur NEUE Treffer melden (Übung 3)
│   ├── sources/
│   │   ├── base.py              # Schnittstelle: so sieht jede Datenquelle aus
│   │   └── mock_source.py       # Demo-Quelle mit Beispieldaten
│   ├── agent/runner.py          # KI-Agent mit Tool Use (Claude API)
│   └── cli.py                   # Kommandozeile: carhunt search / carhunt agent
└── tests/                       # dein Sicherheitsnetz
```

Das wichtigste Architekturmuster hier: **Quellen sind steckbar.** Alles hinter
`sources/base.py` ist austauschbar, ohne dass sich Filter, Speicher oder Agent
ändern. So bauen Profis Systeme, die wachsen können.

## Ad-hoc-Filter: neue Kriterien ohne Codeänderung

Wird dir später z. B. das Alter des Autos wichtig, trägst du einfach eine
Regel in `config/search_profile.yaml` ein – der Code bleibt unangetastet:

```yaml
custom_filters:
  - attribute: first_registration_year
    operator: ">="
    value: 2006
```

Erlaubt sind alle Felder von `CarListing` (models.py) mit den Operatoren
`==`, `!=`, `<`, `<=`, `>`, `>=`. Mehrere Regeln müssen alle zutreffen (UND).
Tippfehler im Attributnamen fliegen sofort beim Laden der Config auf, nicht
erst irgendwann zur Laufzeit – dafür sorgt ein Pydantic-Validator. Wie die
Engine funktioniert, steht in `matches_rule()` in filters.py; das
Python-Schlüsselwort dahinter heißt `getattr`.
**Übung 5:** ergänze einen `contains`-Operator für Textsuche (z. B. „Klima"
in der Beschreibung) – der Test wartet schon in test_filters.py.

## Warum Demo-Daten statt echter Portale?

mobile.de, AutoScout24 & Co. verbieten automatisiertes Auslesen (Scraping) in
ihren Nutzungsbedingungen und blockieren Bots aktiv. Ein Profi baut dagegen
nicht an – er sucht den sauberen Weg. Der sieht so aus: Die Portale bieten
selbst **Suchagenten** an, die dir neue Treffer per E-Mail schicken. Dein
Programm liest in Phase 5 **dein eigenes Postfach** aus und übersetzt diese
Mails in `CarListing`-Objekte. Vollkommen legitim, stabil, und die Architektur
ist dank steckbarer Quellen schon dafür vorbereitet.

---

## Lernpfad

Arbeite die Phasen der Reihe nach ab. Jede Phase hat ein „Fertig, wenn“ –
erst dann weiter. Commit nicht vergessen.

### Phase 0 – Werkzeuge & erster Lauf
Setup wie oben. **Lernziel:** venv, pip, pytest ausführen, erster Git-Commit.

### Phase 1 – Code lesen & Filter erweitern (Übungen 1 + 2)
Lies in dieser Reihenfolge: `models.py` → `filters.py` → `tests/test_filters.py`
→ `cli.py`. Dann:
- **Übung 1:** Alias-Mapping in `normalize_brand()` („Volkswagen" → „vw").
- **Übung 2:** `min_year`-Filter in `matches()` einbauen. (Ginge inzwischen auch
  per Ad-hoc-Filter – bau ihn trotzdem fest ein, damit du `matches()` einmal
  selbst angefasst hast.)

Ablauf pro Übung: Skip-Marker im Test entfernen → `pytest` zeigt Rot →
implementieren → Grün. Das ist Test-Driven Development im Kleinen.
**Fertig, wenn:** alle Filter-Tests grün sind und `carhunt search` plötzlich
**7 Treffer** zeigt – der ausgeschriebene „Volkswagen Golf" für 2.700 € taucht auf.
**Lernziel:** Funktionen, Typen, Pydantic, pytest, Rot-Grün-Zyklus.

### Phase 2 – Ein Gedächtnis (Übung 3)
Implementiere `storage.py` mit SQLite, sodass wiederholte Läufe nur *neue*
Inserate melden. Die Tests in `tests/test_storage.py` beschreiben das Ziel.
Binde das Repository danach in `cmd_search` ein: „davon NEU: …".
**Fertig, wenn:** Storage-Tests grün; zweiter `carhunt search`-Lauf meldet 0 neue.
**Lernziel:** SQL-Grundlagen, Idempotenz, Fixtures (`tmp_path`).

### Phase 3 – Zweite Quelle anstecken
Schreibe eine eigene `ListingSource` (z. B. `CsvSource`, die eine von dir
gepflegte CSV mit echten, von Hand gefundenen Inseraten liest) und lass die CLI
mehrere Quellen nacheinander abfragen.
**Fertig, wenn:** `carhunt search` Treffer aus beiden Quellen kombiniert.
**Lernziel:** Vererbung/Schnittstellen, warum Abstraktion sich auszahlt.

### Phase 4 – Dein erster KI-Agent
API-Key unter https://console.anthropic.com erstellen, als Umgebungsvariable
`ANTHROPIC_API_KEY` setzen, dann `carhunt agent`. Lies danach `agent/runner.py`
Zeile für Zeile – dort ist der komplette Agent-Loop erklärt.
- **Übung 4:** Zweites Tool `get_search_profile` ergänzen.
**Fertig, wenn:** der Agent die Treffer bewertet und du erklären kannst, was
`tool_use` / `tool_result` sind. **Lernziel:** Agent-Loop, Tools, Prompts,
API-Keys sicher handhaben (nie in den Code, nie in Git!).

### Phase 5 – Echte Daten, der saubere Weg
Richte auf 1-2 Portalen deren Suchagenten mit deinen Kriterien ein (Mails an
eine eigene Adresse). Schreibe eine `EmailSource`, die per IMAP (Modul
`imaplib` + `email`) neue Benachrichtigungen liest und in `CarListing` übersetzt.
Zugangsdaten kommen in eine `.env`-Datei (steht schon in `.gitignore`).
**Fertig, wenn:** ein echtes Inserat aus einer Mail in deiner Trefferliste steht.
**Lernziel:** externe Daten parsen, Fehlertoleranz, Umgang mit Geheimnissen.

### Phase 6 – Automatisieren & benachrichtigen
Lass das Programm regelmäßig laufen: Windows-Aufgabenplanung oder `cron` in
der Linux-VM. Bei neuen Treffern: Benachrichtigung (einfachste Variante:
E-Mail an dich selbst; schöner: Telegram-Bot).
**Fertig, wenn:** du morgens ungefragt eine Nachricht mit neuen Treffern bekommst.
**Lernziel:** Scheduling, Logging, ein Programm „in Betrieb" nehmen.

### Phase 7 (optional) – Qualität wie im Team
`ruff check .` in deine Routine aufnehmen, Repository auf GitHub pushen,
GitHub Action einrichten, die bei jedem Push automatisch `pytest` laufen lässt.
**Lernziel:** Linting, CI – der Standard in jedem professionellen Team.

---

## Mit KI arbeiten – die Regeln, die dich wirklich weiterbringen

Du hast einen KI-Assistenten zur Seite. So wird daraus Lernen statt Abschreiben:

1. **Erst 15-30 Minuten selbst versuchen.** Der Lerneffekt entsteht beim Hängen.
2. Bei Fehlern: **Fehlermeldung + Code schicken und um eine *Erklärung* bitten**,
   nicht um die fertige Lösung. („Erkläre mir, was dieser Traceback bedeutet.")
3. Nach jeder Übung: **Code-Review einholen.** („Reviewe das wie ein Senior-
   Entwickler: Was würdest du anders machen und warum?")
4. **Konzepte erklären lassen**, wenn dir etwas im Code fremd ist
   („Was ist eine abstrakte Klasse und warum nutzt base.py eine?").
5. Was die KI liefert, **nie ungelesen übernehmen** – erst verstehen, dann committen.

## Nützliche Befehle

```bash
pytest              # alle Tests
pytest -v           # ausführlich, zeigt auch die Übungs-Skips
ruff check .        # Code-Qualität prüfen
carhunt search      # Suchlauf
carhunt agent       # KI-Bewertung der Treffer (Phase 4)
```
