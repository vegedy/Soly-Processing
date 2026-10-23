# Soly-Processing

Echtzeitverarbeitung und Aggregation von PV- und Batteriedaten mit PyFlink,
eingebunden als Git-Submodule unter `Soly/processing/`. Bisher sind die
Python-Projektgrundlage und ein Import-Smoke-Test eingerichtet; der Flink-Job
folgt separat.

PyFlink 2.2.1 ist für Flink 2.2.1 mit Java 17 vorgesehen. Container-Build,
Kafka-/JDBC-Connectoren und der JVM-/Flink-Integrationstest folgen separat gemäß
`Soly-Technologieentscheidungen.md`.

## Einrichtung

Voraussetzung: **Python 3.12.15**. Alle Befehle im Service-Verzeichnis ausführen.
Falls der Interpreter nicht im Suchpfad liegt, seinen vollständigen Pfad verwenden.

Linux/macOS (Bash/Zsh):

```bash
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Anschließend auf allen Plattformen das Paket editierbar samt pytest, Ruff und
mypy installieren; deren Versionen sind in `pyproject.toml` festgelegt:

```bash
python -m pip install -e ".[dev]"
python -m pip check
```

Für die reproduzierbare Installation unter Linux x86_64 mit Python 3.12.15
stattdessen in der frischen Umgebung die Lockdatei verwenden:

```bash
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e ".[dev]"
python -m pip check
```

Dieser Lockstand wurde in einer zweiten frischen Umgebung geprüft. macOS und
Windows sind nicht verifiziert und können eigene Plattform-Lockstände benötigen.

In neuen Shells die vorhandene Umgebung erneut aktivieren; mit `deactivate`
verlassen. `.venv/`, Caches und Build-Artefakte sind über `.gitignore`
ausgeschlossen. Globale Paketinstallationen sind nicht erforderlich.

## Struktur

```text
src/soly_processing/   Python-Paket
tests/                Import-Smoke-Test und zukünftige Tests
pyproject.toml        Paketmetadaten, Abhängigkeiten und Werkzeugkonfiguration
requirements-dev.lock Festgeschriebene direkte und transitive Abhängigkeiten
.python-version       Einheitliche Python-Version
```

## Prüfungen

In der aktivierten Umgebung:

```bash
python -m pytest                # Tests
python -m ruff check .          # Linting
python -m ruff format --check . # Formatprüfung
python -m mypy src tests        # Typprüfung von Quellcode und Tests
```

Zum automatischen Formatieren: `python -m ruff format .`.

## Abhängigkeiten aktualisieren

Die Lockdatei wird mit `pip freeze` ohne zusätzliches Lock-Werkzeug erzeugt.
Sie fixiert auch transitive Abhängigkeiten sowie pip und setuptools; sie enthält
keine Artefakt-Hashes. Die allgemeine Installation löst transitive Abhängigkeiten
hingegen neu auf.

Nach bewussten Versionsänderungen in einer frischen Python-3.12.15-Umgebung
auf der Zielplattform:

```bash
python -m pip install -e ".[dev]"
python -m pip install "setuptools>=77.0.3"
python -m pip check
python -m pip freeze --all --exclude-editable > requirements-dev.lock
```

Anschließend die Prüfungen und die Installation aus der Lockdatei in einer
weiteren frischen Umgebung nachvollziehen. `--exclude-editable` hält lokale
Projektpfade aus der Datei heraus; der festgeschriebene Build-Backend wird bei
der Installation mit `--no-build-isolation` verwendet.
