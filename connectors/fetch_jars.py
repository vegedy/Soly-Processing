"""Download the Maven-resolved runtime closure and verify every artifact."""

import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen


def main() -> None:
    directory = Path(__file__).resolve().parent
    lock = json.loads((directory / "jars.lock.json").read_text())
    if hashlib.sha256((directory / "pom.xml").read_bytes()).hexdigest() != lock["pom_sha256"]:
        raise RuntimeError("pom.xml changed: regenerate and review the connector lock")
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    for artifact in lock["artifacts"]:
        path = artifact["path"]
        with urlopen(f"https://repo.maven.apache.org/maven2/{path}", timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            raise RuntimeError(f"Checksum mismatch for {path}")
        target = destination / Path(path).name
        if target.exists():
            raise RuntimeError(f"Duplicate artifact filename: {target.name}")
        target.write_bytes(data)
        print(target.name, flush=True)


if __name__ == "__main__":
    main()
