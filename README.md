# Soly-Processing

Python-Paket und gemeinsames Flink-Laufzeitimage für JobManager und TaskManager.
Der fachliche Flink-Job, Kafka-Konsum, Datenbank-Schreibvorgänge und der vollständige
Pipeline-Test folgen separat. Der aktuelle Container-Smoke-Test prüft die Laufzeit
und die Planung mit den Connectoren ohne externe Dienste oder Zugangsdaten.

## Lokale Einrichtung und Prüfungen

Voraussetzung: **Python 3.12.15**, **Java 17** und ein passendes `JAVA_HOME`.
Geprüfte Plattform: **Linux x86_64**. Alle Befehle im Service-Checkout ausführen;
das Hauptrepo ist dafür nicht erforderlich. macOS und Windows sind nicht verifiziert
und können eigene Plattform-Lockstände benötigen.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes --only-binary=:all: -r requirements/build.txt
python -m pip install --require-hashes --no-build-isolation -r requirements/dev.txt
python -m pip install --no-deps --no-build-isolation -e ".[dev]"
python -m pip check
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src tests
```

Für die PowerShell-Umgebung die ersten beiden Befehle durch
`py -3.12 -m venv .venv` und `.\.venv\Scripts\Activate.ps1` ersetzen.
Die übrigen Prüfkommandos sind identisch. Globale Paketinstallationen sind unnötig.
Mit `deactivate` die Umgebung verlassen; in neuen Shells wieder aktivieren.

Die Toolversionen bleiben pytest **9.1.1**, Ruff **0.17.2** und mypy **2.4.0**.
Einige PyFlink-Abhängigkeiten werden nur als Quellpakete bereitgestellt. Deshalb
zuerst den festgeschriebenen Build-Backend installieren und danach mit
`--no-build-isolation` arbeiten. Fremdartefakte werden anhand der SHA-256-Hashes
geprüft; es wird keine zusätzliche ungepinnte Build-Umgebung erzeugt.

## Docker-Build und Smoke-Test

Voraussetzung ist eine laufende Docker Engine. Ein frischer Service-Checkout ohne
Hauptrepo und ohne `.venv` genügt. Der Build benötigt Netzwerkzugriff auf die
festgelegten Paketquellen; der Smoke-Test benötigt keinen Netzwerkzugriff.

```bash
docker build --platform linux/amd64 --tag soly-processing:local .
docker run --rm --network none --hostname localhost --workdir /tmp --entrypoint /opt/python/bin/python3 soly-processing:local -I /opt/soly/smoke_test.py
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
docker run -d --name soly-jobmanager --network soly-processing-local -e JOB_MANAGER_RPC_ADDRESS=soly-jobmanager soly-processing:local jobmanager
docker run -d --name soly-taskmanager --network soly-processing-local -e JOB_MANAGER_RPC_ADDRESS=soly-jobmanager soly-processing:local taskmanager
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
hashgesicherten Installation laufen `pip check`, pytest, Ruff-Linting,
Ruff-Formatprüfung und mypy für `src` und `tests`.

**Docker-Build und Laufzeit-Smoke-Test laufen ausschließlich bei Pushes auf `main`**
und erst nach erfolgreichen Python-Prüfungen. Beide verwenden die oben gezeigten
Build-/Smoke-Kommandos. Fehler lassen den Workflow fehlschlagen. Die Actions sind
über Commits fixiert, Berechtigungen auf `contents: read` begrenzt. Es werden keine
Images in eine Registry veröffentlicht und keine produktiven Secrets benötigt.

## Abhängigkeiten bewusst aktualisieren

Python-Locks mit Python **3.12.15** und **pip-tools 7.5.2** in einer separaten
Umgebung (`.venv-lock`, Aktivierung wie oben) erzeugen. Die bisherigen Constraints
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
