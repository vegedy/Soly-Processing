# Soly-Processing

Echtzeitverarbeitung und Aggregation von PV- und Batteriedaten mit PyFlink,
eingebunden als Git-Submodule unter `Soly/processing/`. Dieses Setup richtet
das Python-Projektfundament ein; der Flink-Job folgt separat.

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

In neuen Shells die vorhandene Umgebung erneut aktivieren; mit `deactivate`
verlassen. `.venv/`, Caches und Build-Artefakte sind über `.gitignore`
ausgeschlossen. Globale Paketinstallationen sind nicht erforderlich.

