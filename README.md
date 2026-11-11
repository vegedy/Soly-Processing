# Soly-Processing

Python-Paket und gemeinsames Flink-Laufzeitimage für JobManager und TaskManager.
Der fachliche Flink-Job, Kafka-Konsum, Datenbank-Schreibvorgänge und der vollständige
Pipeline-Test folgen separat. Der aktuelle Container-Smoke-Test prüft die Laufzeit
und die Planung mit den Connectoren ohne externe Dienste oder Zugangsdaten.

## Entwicklungsbefehle

**Windows:** Entwicklung über WSL2 mit `./dev.sh` im Linux-Checkout,
oder `docker-smoke` mit Linux-Containern. Native Windows-/macOS-Aufrufe
von `setup`, `check` und `format` werden abgelehnt.

Voraussetzung für lokale Entwicklung: **Python 3.12.x** (z. B. 3.12.10). `dev.sh` (POSIX-Shell unter Unix) und `dev.ps1`
(PowerShell 7 unter Linux) delegieren an `scripts/dev.py` mit
Python-Standardbibliothek. Lokal sind alle 3.12-Patchversionen zugelassen.
**CI und Docker bleiben auf Python 3.12.15 festgelegt**; Locks und Image-Pins
werden nicht verändert. Jeder Checkout besitzt eine eigene `.venv`; Aktivierung
ist unnötig. Die Befehle bestimmen den Repository-Pfad selbst. Auch ein Aufruf aus
einem anderen Verzeichnis oder ein Checkout-Pfad mit Leerzeichen funktioniert:

```bash
"/pfad mit Leerzeichen/Soly-Processing/dev.sh" setup
"/pfad mit Leerzeichen/Soly-Processing/dev.sh" check
```

Im Repository unter Unix:

```bash
./dev.sh setup
./dev.sh check
./dev.sh format
```

Unter PowerShell 7 innerhalb von Linux:

```powershell
.\dev.ps1 setup
.\dev.ps1 check
.\dev.ps1 format
# Aus einem anderen Verzeichnis:
& '/pfad mit Leerzeichen/Soly-Processing/dev.ps1' check
```

| Befehl | Wirkung |
|---|---|
| `setup` | Erstellt oder verwendet `.venv`, installiert vorhandene Hash-Locks und prüft Abhängigkeiten. Erneut ausführbar; keine Lock-Neuauflösung. |
| `check` | `pip check`, pytest, Ruff-Linting, Ruff-Formatprüfung und mypy einschließlich `scripts/`; stoppt beim ersten Fehler. |
| `format` | Schreibt ausdrücklich Ruff-Formatänderungen in Projektdateien. |
| `docker-smoke` | Baut `linux/amd64` als `soly-processing:dev-smoke` und führt den vorhandenen isolierten Container-Smoke-Test aus. |

`check` formatiert keine Dateien und legt Tool-Caches/Bytecode nicht im Checkout
an. Externe Fehlercodes werden weitergegeben. Kein Befehl aktualisiert Submodule,
löscht lokale Daten oder verändert globale Systemeinstellungen.

`docker-smoke` überspringt die lokale `.venv` und verwendet einen Host-Interpreter;
`SOLY_PYTHON` bleibt als ausdrückliche Vorgabe vorrangig.

Interpreterwahl: `SOLY_PYTHON` (ein vollständiger Dateipfad, keine zusätzlichen
Argumente), vorhandene `.venv`, dann `python3.12`/`python3`/`python` unter Unix;
PowerShell versucht vor den Python-Befehlen zusätzlich `py -3.12`. Eine ungeeignete
Python-Version oder unvollständige `.venv` führt zu einem Hinweis, nicht zum
Löschen/Ersetzen. Bei Bedarf die vorhandene Umgebung zuerst selbst prüfen und
beiseitelegen. Einen bestimmten Interpreter auswählen:

```bash
SOLY_PYTHON='/pfad zu Python/bin/python3.12' ./dev.sh setup
```

```powershell
$env:SOLY_PYTHON = '/pfad zu Python/bin/python3.12'
.\dev.ps1 setup
```

Falls die lokale PowerShell-Richtlinie Skripte sperrt, die geltende Richtlinie
prüfen oder den Python-Einstieg direkt aufrufen; die Skripte ändern keine
Sicherheitseinstellungen und verwenden keinen Execution-Policy-Bypass:

```powershell
python3.12 scripts/dev.py setup
& ./.venv/bin/python scripts/dev.py check
```

Die CI nutzt `setup --use-current-python` und `check --use-current-python` mit dem
bereits durch Actions eingerichteten Python. Lokal erlaubt `setup` diese Option
nur in einer virtuellen Umgebung; außerhalb davon ist sie ausschließlich mit
`CI=true` vorgesehen. Normalerweise ohne diese Option arbeiten. Die Skripte und
Textdateien verwenden festgelegte Zeilenenden; Vertragsartefakte behalten über
`.gitattributes` ihre exakten Bytes.

Processing-Entwicklung ist auf **Linux x86_64** begrenzt. Zusätzlich sind
**Java 17**, ein passendes `JAVA_HOME` und die für PyFlink-Quellpakete benötigten
Buildwerkzeuge erforderlich. Unter Windows **WSL2** nutzen, den Checkout im
Linux-Dateisystem ablegen und dort `./dev.sh setup` / `./dev.sh check` ausführen.
Native Windows-/macOS-Aufrufe von `setup`, `check` und `format` werden mit einem
Hinweis abgelehnt. Alternativ von Windows/macOS `docker-smoke` mit Docker Desktop
und Linux-Containern nutzen. Der Host braucht dafür weder Java 17 noch PyFlink;
eine lokale `.venv` ist unnötig. Es wird keine native Plattformunterstützung behauptet.

`setup` installiert zuerst `requirements/build.txt` als gehashte Wheels, dann
`requirements/dev.txt` mit `--require-hashes --no-build-isolation`, anschließend
das eigene Paket mit `--no-deps --no-build-isolation -e ".[dev]"`.
Der Dev-Lock wird wegen der PyFlink-Quellabhängigkeiten nicht auf Wheels beschränkt.
Die Prüfung von Java 17 erfolgt vor der Installation.

## Docker-Build und Smoke-Test

Voraussetzung ist eine laufende Docker Engine. Ein frischer Service-Checkout ohne
Hauptrepo und ohne `.venv` genügt; der Wrapper benötigt einen Python-Interpreter
(empfohlen 3.12.x). Der Build benötigt Netzwerkzugriff auf die
festgelegten Paketquellen; der Smoke-Test benötigt keinen Netzwerkzugriff.

```bash
./dev.sh docker-smoke
# PowerShell: .\dev.ps1 docker-smoke
```

Der Test läuft außerhalb des Quellbaums ohne eingebundene Arbeitsverzeichnisse und
prüft:

- Python **3.12.15**, Flink/PyFlink **2.2.1**, Java **17** und den Import des
  installierten `soly_processing` aus `site-packages`.
- Initialisierung einer lokalen Stream- und Table-Ausführungsumgebung.
- Laden der Kafka-Source-/Factory-, JDBC-Factory-, PostgreSQL-Dialekt- und
  Treiberklassen, einschließlich ihrer Methodensignaturen.
- Planung einer Kafka-Abfrage und eines JDBC-Inserts über die Table API.
  Die verwendeten Platzhalteradressen werden nicht kontaktiert; es wird kein
  Streaming-Job eingereicht und keine Datenbankverbindung geöffnet.

Ein Fehler führt zu einem Fehlercode. Der Test benötigt beschreibbare temporäre
Verzeichnisse für die lokale Java-Gateway-Laufzeit. Er läuft als Benutzer `flink`.

## Festgeschriebene Laufzeit

| Bestandteil | Stand |
|---|---|
| Basis-Image | `flink:2.2.1-java17` |
| Basis-Digest | `sha256:c5124717afe3829cc2d7c9b538bfe0b9d66cae3107a174d8f0e0392abe6375b8` |
| JVM im Basis-Image | Temurin **17.0.20.1+1** |
| Python | **3.12.15**, aus offiziellem Quellarchiv gebaut |
| Python-Quellarchiv SHA-256 | `c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a` |
| Native Pakete | Ubuntu-Noble-Snapshot **20261023T000000Z** |
| PyFlink | **2.2.1** |
| Kafka-Connector | **5.0.0-2.2** |
| JDBC-Core und JDBC-Postgres | **4.1.0-2.2** |
| PostgreSQL-JDBC-Treiber | **42.7.14** |

Image und JVM wurden am **23. Oktober 2026** auf **linux/amd64** geprüft.
Python wird auf demselben Flink-/Ubuntu-Unterbau kompiliert, der später verwendet
wird. Es werden keine Binärdateien aus einer anderen Linux-Distribution kopiert.
Native Systempakete kommen aus dem datierten
[Ubuntu-Snapshot](https://snapshot.ubuntu.com/). Der mehrstufige Build übernimmt
nur Python, die gebauten Python-Wheels und die verifizierten Connector-JARs;
Compiler und Maven sind keine zusätzlich installierten Laufzeitwerkzeuge.

`requirements/runtime.txt` fixiert die direkten und transitiven PyFlink-Abhängigkeiten.
`requirements/dev.txt` ergänzt die Entwicklungswerkzeuge und `requirements/build.txt`
die Buildwerkzeuge. Die bisherigen Paketversionen aus dem SOLY-4-Lock wurden als
`requirements/previous-versions.txt` übernommen; pip und setuptools werden durch
den expliziten Build-Lock vorgegeben. `requirements-dev.lock` verweist zur
Kompatibilität auf den neuen Entwicklungs-Lock. Externe Downloads sind durch
Hashes fixiert; bitweise identische Layer oder Wheel-Zeitstempel werden nicht garantiert.

## JVM-Abhängigkeiten und gewählte API

`connectors/pom.xml` beschreibt die direkten Maven-Abhängigkeiten und
`connectors/dependency-tree.txt` ihre aufgelösten transitiven Laufzeitabhängigkeiten.
Der vollständige Stand mit SHA-256-Hashes liegt in `connectors/jars.lock.json`.
Der Image-Build lädt ausschließlich diese Artefakte von Maven Central und prüft
jeden Hash. Bei geändertem POM ohne erneuerte Lockdatei schlägt er fehl.

Für JDBC wird die **Table API** verwendet. Die modulare Version 4.1.0-2.2 benötigt
sowohl `flink-connector-jdbc-core` als auch `flink-connector-jdbc-postgres` und den
PostgreSQL-Treiber. Der ältere `pyflink.datastream.connectors.jdbc.JdbcSink`-Wrapper
verwendet eine andere JVM-Klassenstruktur und ist mit diesen modularen Artefakten
nicht der gewählte Einstiegspunkt. Die Versionen werden deshalb nicht ausgetauscht.
Siehe auch die [JDBC-Dokumentation](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/connectors/table/jdbc/).

Zusätzlich wird `flink-connector-base` **2.2.1** ergänzt. Die Flink-Kernbibliotheken
und SLF4J kommen aus der Flink-Distribution. Der Jackson-BOM **2.18.2** richtet die
von Kafka und OpenLineage gemeinsam verwendeten Jackson-Module auf einen Stand aus.
Es werden keine zusätzlichen konkurrierenden Flink-Kern- oder Logging-Versionen
in das Image kopiert. Alle Connectoren liegen in `/opt/flink/lib` und stehen so
Client, JobManager und TaskManager zur Verfügung.

## Dasselbe Image für beide Flink-Rollen

Der offizielle Entrypoint und die Flink-Startbefehle bleiben erhalten.
`python.client.executable` und `python.executable` verweisen in der gemeinsamen
Flink-Konfiguration auf `/opt/python/bin/python3`. Zusätzlich ist
`PYFLINK_CLIENT_EXECUTABLE` gesetzt. Beide Rollen verwenden denselben
Python-/Connector-Stand. Die Rollen lassen sich beispielsweise so starten
(Bash, keine produktive Pipeline-Konfiguration):

```bash
docker network create soly-processing-local
docker run -d --name soly-jobmanager --network soly-processing-local -e JOB_MANAGER_RPC_ADDRESS=soly-jobmanager soly-processing:dev-smoke jobmanager
docker run -d --name soly-taskmanager --network soly-processing-local -e JOB_MANAGER_RPC_ADDRESS=soly-jobmanager soly-processing:dev-smoke taskmanager
docker logs soly-jobmanager
docker logs soly-taskmanager
```

Die Beispielcontainer mit `docker stop soly-taskmanager soly-jobmanager` stoppen,
danach mit `docker rm soly-taskmanager soly-jobmanager` entfernen und mit
`docker network rm soly-processing-local` das Beispielnetzwerk aufräumen.
Gesamt-Compose, produktive Job-Einreichung und Checkpoint-Konfiguration folgen separat.
Konfiguration und echte Zugangsdaten werden erst zur Laufzeit übergeben, niemals
in Buildargumente oder Image-Dateien aufgenommen. Der aktuelle Smoke-Test benötigt
keine Secrets. Die `.dockerignore` lässt ausschließlich benötigte Builddateien zu
und schließt insbesondere `.git`, `.venv`, Caches, Checkpoints und lokale Daten aus.

## GitHub Actions

Die Python-Prüfungen laufen bei **jedem Push** und bei **Pull Requests nach `main`**
mit Python **3.12.15**, Java **17** und den lokalen Toolversionen. Nach der
hashgesicherten Installation über `./dev.sh setup --use-current-python` führt
`./dev.sh check --use-current-python` die gemeinsamen Prüfungen aus, einschließlich
der Typprüfung von `src`, `tests` und `scripts`. Die Processing-CI bleibt auf
Ubuntu 24.04; sie behauptet keine native Windows-/macOS-Unterstützung.

**Docker-Build und Laufzeit-Smoke-Test laufen ausschließlich bei Pushes auf `main`**
und erst nach erfolgreichen Python-Prüfungen. Beide laufen über `./dev.sh docker-smoke`. Fehler lassen den Workflow fehlschlagen. Die Actions sind
über Commits fixiert, Berechtigungen auf `contents: read` begrenzt. Es werden keine
Images in eine Registry veröffentlicht und keine produktiven Secrets benötigt.

## Abhängigkeiten bewusst aktualisieren

Python-Locks mit Python **3.12.15** und **pip-tools 7.5.2** in einer separaten
Linux-Umgebung (`python3.12 -m venv .venv-lock`, dann
`source .venv-lock/bin/activate`) erzeugen. Die bisherigen Constraints
bei beabsichtigten Versionswechseln ausdrücklich mit ändern:

```bash
python -m pip install "pip-tools==7.5.2"
python -m piptools compile --generate-hashes --allow-unsafe --strip-extras --output-file requirements/build.txt requirements/build.in
python -m piptools compile --generate-hashes --allow-unsafe --strip-extras --constraint requirements/previous-versions.txt --output-file requirements/runtime.txt pyproject.toml
python -m piptools compile --generate-hashes --allow-unsafe --strip-extras --constraint requirements/previous-versions.txt --extra dev --output-file requirements/dev.txt pyproject.toml requirements/dev.in
```

Connectoren nach bewusster Anpassung des POM mit dem festgeschriebenen Maven-Image
und Dependency-Plugin neu auflösen (Bash, nur diese Aktualisierung benötigt Maven):

```bash
docker run --rm --user "$(id -u):$(id -g)" -e MAVEN_CONFIG=/tmp/maven -v "$PWD:/work" -w /work maven:3.9.9-eclipse-temurin-17@sha256:f58d59b6273e785ac0a4477f6e9b5ba1d7731c75b906c0f7b34076f1851318cc mvn -B -f connectors/pom.xml -Dmaven.repo.local=/tmp/m2 org.apache.maven.plugins:maven-dependency-plugin:3.8.1:copy-dependencies -DincludeScope=runtime -DoutputDirectory=/work/connectors/target/jars org.apache.maven.plugins:maven-dependency-plugin:3.8.1:tree -DoutputFile=/work/connectors/dependency-tree.txt
python connectors/lock_jars.py
```

Den Abhängigkeitsbaum und alle Hashänderungen prüfen, anschließend die
Python-Installation in einer frischen Umgebung und den vollständigen Docker-Build
samt Laufzeit-Smoke-Test nachvollziehen. Basis-Digest, Python-Quellhash und
Ubuntu-Snapshot werden nur gemeinsam mit erneuter Laufzeitprüfung aktualisiert.


## Validierung von SOLY-18

Am **3. November 2026** unter **Linux x86_64**, Python **3.12.15** und
**PowerShell 7.5.4** tatsächlich ausgeführt: frischer eigenständiger Checkout in
einem Pfad mit Leerzeichen, `setup` über Unix und PowerShell erneut ausgeführt,
`check` und `format` über beide Einstiege, außerdem `setup/check` mit
`--use-current-python`. Alle Prüfungen erfolgreich (**15 Tests**, pip check,
Ruff und mypy). Dateiinhalt und Änderungszeit der Projektdateien blieben bei
beiden `check`-Aufrufen unverändert. Fehlercodes, unvollständige Umgebungen,
fehlende Werkzeuge und Plattformhinweise sind zusätzlich durch Regressionstests
abgedeckt. `./dev.sh docker-smoke` wurde auf **linux/amd64** erfolgreich ausgeführt.
Locks, Laufzeitpins und der bestehende Container-Smoke-Test wurden nicht geändert.

Die lokale Processing-Prüfung verwendete `JAVA_HOME` mit **OpenJDK 17**;
der Container prüfte **Temurin 17.0.20.1**, PyFlink 2.2.1 und die vorhandenen
Kafka-/JDBC-Pläne. Native Windows-/macOS- und WSL2-Ausführung wurden lokal nicht
getestet. WSL2 ist der beschriebene Linux-Weg, kein separat erbrachter Nachweis.

## Unterstützter Ereignisvertrag

Dieser Service unterstützt **Soly event contract v1**.

Konsumiert den Kafka-Vertrag, prüft Version und Key, bewertet Sensorzustände und verantwortet fachliche Normalisierung, Event-Time-Verarbeitung und Energieintegration.
Diese Rolle beschreibt die vorgesehene Schnittstelle; die fachliche
Service-Implementierung und Laufzeitvalidierung folgen in eigenen Issues.

Die [maßgebliche Spezifikation](https://github.com/vegedy/Soly/blob/abd467e82f1bf57279ae3c14a01a765389daad90/docs/data-contract.md)
ist auf einen unveränderlichen, veröffentlichten Hauptrepo-Commit festgeschrieben.
[contracts/v1/](contracts/v1/) enthält eine identische lokale Kopie aller Schemata,
des Sensorkatalogs und der synthetischen Beispiele. Der eigenständige Checkout
benötigt dafür weder das Hauptrepo noch benachbarte Services.
[contracts/provenance.json](contracts/provenance.json) nennt unterstützte Version,
Herkunftsrepository, vollständigen Commit und SHA-256-Prüfsummen aller Dateien.
Es gibt keine Schema-Downloads beim Start und keine Laufzeitimporte aus Submodulen.

Veröffentlichte v1-Artefakte bleiben unverändert. Änderungen am Vertragsverhalten
benötigen eine neue Version; unbekannte Versionen werden künftig ausdrücklich
abgelehnt. Eine Vertragsaktualisierung übernimmt alle Artefakte und das
Herkunftsmanifest gemeinsam und wird mit den zentralen Vertragsprüfungen geprüft.
Der abschließende Hauptrepo-CI-Lauf kontrolliert die Kopie und ihre Herkunft.

## Mitarbeit und Arbeitsregeln

[AGENTS.md](AGENTS.md) enthält die kurzen Arbeitsregeln für diesen eigenständigen
Service. Die zentrale [Beitragsanleitung](https://github.com/vegedy/Soly/blob/main/CONTRIBUTING.md)
und der [Git-Workflow](https://github.com/vegedy/Soly/blob/main/Soly-Issue-und-Git-Workflow.md)
erklären Issues, SOLY-Branches, Service-PRs und die anschließende Submodule-Integration.
Die [Technologieentscheidungen](https://github.com/vegedy/Soly/blob/main/Soly-Technologieentscheidungen.md)
unterscheiden historische Auswahl und implementierten Stand.

Die CI prüft zusätzlich den lokalen Setup-Weg in einem frischen Checkout mit
Leerzeichen: Unix-Setup, erneutes PowerShell-Setup mit Erhalt der bestehenden
`.venv`, danach `check` über beide Einstiege ohne `--use-current-python`.
Alle Aufrufe dieses Jobs erfolgen außerhalb des Checkout-Verzeichnisses.
