# Arbeiten an Soly-Processing

- Eigenständiges Repository; im Hauptrepo als `processing/` eingebunden.
  Verantwortet künftig Kafka-Konsum, fachliche Normalisierung, Event-Time-Energieintegration und PostgreSQL-Ergebnisse. JDBC nutzt die Table API mit den modularen Connectoren; nicht auf den älteren DataStream-JDBC-Wrapper ausweichen.
  Aktuell bestehen Paketgrundlage, Container-Smoke-Test, CI und Vertragskopien;
  die fachliche Implementierung folgt separat. Code unter `src/`, Tests in `tests/`.
- Einrichtung, Locks und Docker-Kommandos: [README.md](README.md).
  Python 3.12.15 mit eigener `.venv` verwenden. Java 17 mit passendem `JAVA_HOME` verwenden. Zuerst den Build-Lock als Wheels installieren, dann den Dev-Lock mit `--no-build-isolation`, anschließend das eigene Paket ohne Abhängigkeitsauflösung installieren. Nicht den gesamten Dev-Lock auf Wheels beschränken: PyFlink hat Quell-Abhängigkeiten. Linux x86_64 ist die geprüfte Plattform.
- Issues zentral in [vegedy/Soly](https://github.com/vegedy/Soly/issues).
  Vollständiger Ablauf: [CONTRIBUTING.md](https://github.com/vegedy/Soly/blob/main/CONTRIBUTING.md),
  [Git-Workflow](https://github.com/vegedy/Soly/blob/main/Soly-Issue-und-Git-Workflow.md),
  [Technologieentscheidungen](https://github.com/vegedy/Soly/blob/main/Soly-Technologieentscheidungen.md).
  Diese Links benötigen keinen lokalen Hauptrepo-Checkout und sind nach Integration
  des zugehörigen Hauptrepo-PRs verfügbar.
- Vor Änderungen einen aktiven Branch von aktuellem `origin/main` anlegen:
  `SOLY-<Nummer>_<beschreibung>` (klein, Unterstriche). Submodule können im detached
  HEAD stehen. Commits und PR-Titel auf Englisch mit `SOLY-<Nummer>` beginnen.
  Service-PR nach `main` mit `Refs vegedy/Soly#<Nummer>`, ohne Abschlussverweis.
  Review und Merge übernimmt der Nutzer; PRs weder selbst freigeben noch mergen.
  Danach wird der gemergte Commit im Hauptrepo integriert; erst dessen abschließender
  PR verwendet `Closes #<Nummer>`.
- Verbindlich ist die in der [README](README.md#unterstützter-ereignisvertrag)
  auf einen veröffentlichten Commit fixierte Spezifikation. `contracts/v1/` und
  [contracts/provenance.json](contracts/provenance.json) sind lokale Vertragskopien
  samt Herkunft; veröffentlichte v1-Artefakte nicht verändern. Neue Semantik braucht
  eine neue Version. Aktualisierte Kopien, Manifest und Spezifikationslink gemeinsam
  übernehmen; im Hauptrepo Vertrags- und `service_copies`-Prüfungen ausführen.
  Keine Laufzeitimporte aus Nachbarrepos oder Schema-Downloads beim Start.
- Im Service nach README-Einrichtung prüfen: `python -m pip check`,
  `python -m pytest`, `python -m ruff check .`, `python -m ruff format --check .`,
  `python -m mypy src tests`. CI führt diese Prüfungen bei Push/PR aus;
  Docker-Build/Smoke-Test nur bei Push auf `main`. Bei Änderungen an Laufzeit,
  Abhängigkeiten oder Container zusätzlich Docker-Build und Smoke-Test nach README.
- Laufzeitpins, Hash-Locks und Image-Digests nur bewusst mit Begründung und erneuter
  Validierung ändern; Generatoren stehen in der README. Keine Secrets, privaten
  Rohdaten, lokalen Umgebungen oder Caches einchecken. Im PR tatsächliche Tests und
  Einschränkungen nennen; keine Ende-zu-Ende-Garantie aus einem Smoke-Test ableiten.
