#!/usr/bin/env python3
"""Entry program for the make.fun news-image-20261118 bounty.

The entry image is bundled next to this file as ``entry.png``. Running
this program copies that image, byte for byte, to
``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output`` when the variable is
not set). It uses only the Python standard library, needs no network,
and always produces the same bytes, so repeated runs are identical.
"""

import os
import shutil
import sys


def main():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "entry.png")
    if not os.path.isfile(source):
        print("error: entry.png is missing next to main.py", file=sys.stderr)
        sys.exit(1)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    # Guard against a truncated copy: the output must be the same size
    # as the bundled image, otherwise fail loudly instead of handing
    # the grader a broken file.
    if os.path.getsize(target) != os.path.getsize(source):
        print("error: copied entry.png has the wrong size", file=sys.stderr)
        sys.exit(1)
    print("wrote", target)


if __name__ == "__main__":
    main()
