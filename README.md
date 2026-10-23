# Soly-Processing

Echtzeitverarbeitung und Aggregation von PV- und Batteriedaten mit PyFlink,
eingebunden als Git-Submodule unter `Soly/processing/`. Bisher sind das
Python-Projektfundament und ein Import-Smoke-Test eingerichtet; der Flink-Job
folgt separat.

## Versionen

Wie in `Soly-Technologieentscheidungen.md` festgelegt:

| Komponente | Version |
|---|---|
| Python | 3.12.15 |
| PyFlink (`apache-flink`) | 2.2.1 |
| pytest | 9.1.1 |
| Ruff | 0.17.2 |
| mypy | 2.4.0 |

Python ist in `.python-version` und `pyproject.toml` festgelegt. Metadaten,
Runtime- und Dev-Abhängigkeiten sowie Werkzeugkonfigurationen folgen dem
Simulator-Projekt; Processing ergänzt PyFlink als Laufzeitabhängigkeit.

## Einrichtung

Alle Befehle im Service-Verzeichnis ausführen. Der verwendete Interpreter muss
**Python 3.12.15** sein; vor dem Erstellen der Umgebung die Ausgabe prüfen.
Falls er nicht im Suchpfad liegt, seinen vollständigen Pfad verwenden.

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

Für die reproduzierbare Einrichtung unter **Linux x86_64 mit CPython 3.12.15**
werden zunächst alle festgeschriebenen Abhängigkeiten einschließlich pip und
setuptools installiert. Anschließend wird das eigene Paket editierbar installiert,
ohne Abhängigkeiten oder den Build-Backend erneut aufzulösen:

```bash
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e ".[dev]"
python -m pip check
```

Die allgemeine Installation mit den direkten Versionsvorgaben ist alternativ:

```bash
python -m pip install -e ".[dev]"
python -m pip check
```

Dabei werden transitive Abhängigkeiten neu aufgelöst. Der eingecheckte Lockstand
ist für Linux x86_64 geprüft; macOS und Windows sind nicht verifiziert und können
eigene Plattform-Lockstände benötigen.

In neuen Shells die vorhandene Umgebung erneut aktivieren; mit `deactivate`
verlassen. `.venv/`, Caches und Build-Artefakte sind über `.gitignore`
ausgeschlossen. Globale Paketinstallationen sind nicht erforderlich.

## Struktur

```text
src/soly_processing/ Python-Paket
tests/              Import-Smoke-Test und zukünftige Tests
pyproject.toml       Paketmetadaten, Abhängigkeiten und Werkzeugkonfiguration
requirements-dev.lock Direkte und transitive Abhängigkeiten samt Build-Werkzeug
.python-version      Einheitliche Python-Version
```

## Prüfungen

In der aktivierten Umgebung:

```bash
python -m pytest                # Tests
python -m ruff check .           # Linting
python -m ruff format --check .  # Formatprüfung
python -m mypy src tests         # Strikte Typprüfung von Quellcode und Tests
python -m pip check              # Konsistenz der installierten Abhängigkeiten
```

Zum automatischen Formatieren: `python -m ruff format .`.
Der Smoke-Test importiert das installierte Paket ohne zusätzliche Suchpfade.

Am 23. Oktober 2026 unter Linux x86_64 mit Python 3.12.15 geprüft: allgemeine
Installation und anschließende Lock-Installation in einer zweiten frischen
Umgebung, identischer Paketstand, ein erfolgreicher Smoke-Test sowie alle oben
aufgeführten Prüfungen. Das eigene Paket und PyFlink ließen sich auch außerhalb
des Projektverzeichnisses importieren. Ein JVM-/Flink-Integrationstest steht aus.

## Abhängigkeiten aktualisieren

Als einfaches Verfahren ohne zusätzliches Lock-Werkzeug dient ein vollständiger
`pip freeze --all --exclude-editable`-Stand. Die Datei fixiert direkte und transitive
Runtime- und Dev-Abhängigkeiten sowie pip und setuptools auf konkrete Versionen.
Das eigene Paket bleibt über die editierbare Installation eingebunden; lokale
absolute Pfade werden nicht im Lockstand gespeichert. Die Datei fixiert
Paketversionen, enthält aber keine Artefakt-Hashes.

Einen neuen Stand nach bewussten Versionsänderungen in einer **frischen**
Python-3.12.15-Umgebung auf der Zielplattform erzeugen:

```bash
python -m pip install -e ".[dev]"
python -m pip install "setuptools>=77.0.3"
python -m pip check
python -m pip freeze --all --exclude-editable > requirements-dev.lock
```

Anschließend die Prüfungen ausführen und die Installation aus der Lockdatei in
einer weiteren frischen Umgebung nachvollziehen. Erst danach den neuen Stand
committen. Der Build-Backend ist im Lockstand enthalten, damit die Installation
mit `--no-build-isolation` dieselbe setuptools-Version verwendet.

## Flink-Laufzeit und nächste Integrationsschritte

PyFlink 2.2.1 ist für die gemeinsame Laufzeit **Flink 2.2.1 / Java 17** vorgesehen.
Die Python-Installation allein stellt noch keinen eingerichteten Flink-Cluster dar.
Das spätere Processing-Image muss Python 3.12.15 ergänzen und für JobManager und
TaskManager identisch sein.

Der JVM-/Container-Build, Kafka-Connector **5.0.0-2.2**, JDBC-Connector
**4.1.0-2.2** einschließlich benötigter Module und transitiver Abhängigkeiten
sowie PostgreSQL-JDBC **42.7.14** folgen als eigener Integrationsschritt.
Flink-Job-Ausführung, Event-Time-Verarbeitung und PostgreSQL-Sink sind ebenfalls
nicht Teil dieses Python-Setups.
