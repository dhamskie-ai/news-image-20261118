#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261118 submission.

Copies the pre-rendered front page (entry.png, in this repo) into the
output directory requested by the harness and proves the copy is exact.

Behaviour:
  * source: entry.png next to this file
  * target: $MAKEFUN_OUTPUT_DIR/entry.png, or /output/entry.png when
    the variable is unset
  * checks: PNG magic bytes on the source and on the copy, plus a
    SHA-256 comparison between source and copy
  * exits non-zero with a clear message if anything fails
"""
import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


def png_dimensions(path: Path) -> tuple[int, int]:
    """Read width/height from the IHDR chunk of a PNG file.

    Pure stdlib: PNG files start with the 8-byte magic, then an IHDR
    chunk whose 13-byte payload begins with width and height as
    big-endian unsigned 32-bit integers.
    """
    with path.open("rb") as handle:
        header = handle.read(8 + 4 + 4 + 13)
    if len(header) < 29 or header[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file (bad magic bytes)")
    chunk_length = struct.unpack(">I", header[8:12])[0]
    chunk_type = header[12:16]
    if chunk_length != 13 or chunk_type != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> "SystemExit":
    print(f"main.py: ERROR: {message}", file=sys.stderr)
    return SystemExit(1)


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"

    if not source.is_file():
        raise SystemExit(fail(f"source image missing: {source}"))

    with source.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        raise SystemExit(fail("source is not a PNG file (bad magic bytes)"))
    try:
        width, height = png_dimensions(source)
    except ValueError as exc:
        raise SystemExit(fail(f"source PNG is malformed: {exc}"))
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(
            fail(f"source is {width}x{height}, expected "
                 f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"))
    source_hash = sha256_of(source)
    source_size = source.stat().st_size
    if source_size > 1024 * 1024:
        raise SystemExit(
            fail(f"source is {source_size} bytes, over the 1 MiB limit"))

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"

    shutil.copyfile(source, target)

    with target.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        raise SystemExit(fail("copied file is not a PNG (bad magic bytes)"))
    target_hash = sha256_of(target)
    if target_hash != source_hash:
        raise SystemExit(
            fail(f"SHA-256 mismatch after copy: {target_hash} != "
                 f"{source_hash}"))

    print(f"main.py: wrote {target}")
    print(f"main.py: bytes {source_size}")
    print(f"main.py: sha256 {target_hash}")
    print("main.py: OK — copy verified byte-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
