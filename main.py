#!/usr/bin/env python3
"""THE COMPASS ROSE - News Image 24 November 2026 (Akun 19, @retteangs1).

Entrypoint for the make.fun competition news-image-20261124. The front
page itself is entry.png in this same repository, drawn in-session by
compose.py (PIL build-time script) from the locked NI24 news pool. This
program only carries it to the grader's output directory: standard
library only, no network, deterministic - the same bytes on every run.

Before copying it enforces the competition gate in code: the file must
be a real PNG, exactly 1024x1024 pixels, and at most 1 MiB.
"""
import hashlib
import os
import struct
import sys

MAX_BYTES = 1048576
WANT_WIDTH = 1024
WANT_HEIGHT = 1024


def entry_bytes():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    with open(path, "rb") as fh:
        return fh.read()


def check_png(data):
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if data[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
        raise SystemExit("entry.png must be exactly 1024x1024, got %dx%d"
                         % (width, height))
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png exceeds 1 MiB: %d bytes" % len(data))
    return width, height


def output_dir():
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return env
    if os.path.isdir("/output"):
        return "/output"
    return "out"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check-only" in argv
    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    data = entry_bytes()
    width, height = check_png(data)
    digest = hashlib.sha256(data).hexdigest()
    if check_only:
        print("check-only: entry.png %dx%d, %d bytes, sha256 %s - OK"
              % (width, height, len(data), digest))
        return 0
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as fh:
        fh.write(data)
    with open(dest, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != digest:
        raise SystemExit("copy verification failed: bytes differ")
    print("entry.png: %dx%d, %d bytes, sha256 %s"
          % (width, height, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
