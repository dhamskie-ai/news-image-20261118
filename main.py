#!/usr/bin/env python3
"""Ship the bundled newspaper picture to the grader's output folder.

Next to this script lives a finished PNG of a one-page newspaper
covering world news from 18 November 2026. All this script does is
hand that exact file over: it locates the PNG beside itself, drops a
byte-identical duplicate at ``$MAKEFUN_OUTPUT_DIR/entry.png`` (falling
back to ``/output`` when the variable is absent), and then proves the
duplicate matches by comparing SHA-256 digests. Nothing here touches
the network, nothing is generated on the fly, and running it twice
always yields the same bytes.
"""

import hashlib
import os
import sys
from pathlib import Path


def resolve_paths():
    """Work out where the bundled picture is and where its copy goes."""
    here = Path(__file__).resolve().parent
    bundled = here / "entry.png"
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    return bundled, folder / "entry.png"


def digest(path):
    """Return the SHA-256 hex digest of the file at ``path``."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_checked(bundled, destination):
    """Duplicate ``bundled`` at ``destination`` and prove it matches."""
    if not bundled.is_file():
        print(f"fatal: no entry.png found beside {__file__}", file=sys.stderr)
        raise SystemExit(1)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"fatal: cannot create output folder: {exc}", file=sys.stderr)
        raise SystemExit(1)
    expected = digest(bundled)
    data = bundled.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("fatal: bundled entry.png does not start with a PNG header",
              file=sys.stderr)
        raise SystemExit(1)
    destination.write_bytes(data)
    actual = digest(destination)
    if actual != expected:
        print("fatal: copy failed integrity check (sha256 mismatch)",
              file=sys.stderr)
        raise SystemExit(1)
    print(f"wrote {destination} ({len(data)} bytes, sha256 {actual})")


def main():
    bundled, destination = resolve_paths()
    copy_checked(bundled, destination)


if __name__ == "__main__":
    main()
