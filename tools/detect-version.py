import os
import json
from pathlib import Path
import sys
from typing import Iterator


SOURCE_ROOT = Path(__file__).resolve().parent.parent


def detect_version() -> str:
    haku_identity = SOURCE_ROOT / "haku/upstream.json"
    if haku_identity.exists():
        # Haku release tags name the fork; the core protocol version stays pinned.
        return json.loads(haku_identity.read_text())["frida_protocol_version"]
    releng_location = next(enumerate_releng_locations(), None)
    if releng_location is not None:
        sys.path.insert(0, str(releng_location.parent))
        from releng.frida_version import detect
        version = detect(SOURCE_ROOT).name
    else:
        version = "0.0.0"
    return version


def enumerate_releng_locations() -> Iterator[Path]:
    val = os.environ.get("FRIDA_RELENG")
    if val is not None:
        custom_releng = Path(val)
        if releng_location_exists(custom_releng):
            yield custom_releng

    val = os.environ.get("MESON_SOURCE_ROOT")
    if val is not None:
        parent_releng = Path(val) / "releng"
        if releng_location_exists(parent_releng):
            yield parent_releng

    local_releng = SOURCE_ROOT / "releng"
    if releng_location_exists(local_releng):
        yield local_releng


def releng_location_exists(location: Path) -> bool:
    return (location / "frida_version.py").exists()


if __name__ == "__main__":
    print(detect_version())
