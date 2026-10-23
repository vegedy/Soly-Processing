"""Record checksums of the Maven-resolved runtime closure after an explicit update."""

import hashlib
import json
import re
from pathlib import Path


def main() -> None:
    directory = Path(__file__).resolve().parent
    tree = (directory / "dependency-tree.txt").read_text()
    artifacts = []
    for group, artifact, version, _scope in re.findall(
        r"([\w.\-]+):([\w.\-]+):jar:([^:\s]+):(compile|runtime)", tree
    ):
        name = f"{artifact}-{version}.jar"
        jar = directory / "target" / "jars" / name
        artifacts.append(
            {
                "path": f"{group.replace('.', '/')}/{artifact}/{version}/{name}",
                "sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
            }
        )
    if not artifacts:
        raise RuntimeError("No runtime artifacts found in the Maven dependency tree")
    lock = {
        "pom_sha256": hashlib.sha256((directory / "pom.xml").read_bytes()).hexdigest(),
        "artifacts": sorted(artifacts, key=lambda item: item["path"]),
    }
    (directory / "jars.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    print(f"Locked {len(artifacts)} runtime artifacts")


if __name__ == "__main__":
    main()
