#!/usr/bin/env python3
"""THE TRADE WINDS POST - make.fun news-image-20261124 entry (Akun 19).

Standard-library-only carrier. It opens entry.png in this directory,
enforces the gate in code (real PNG, exactly 1024x1024, at most 1 MiB),
and writes the PNG bytes out exactly as stored: to
$MAKEFUN_OUTPUT_DIR/entry.png when that variable is set, otherwise to
standard output as raw bytes.
"""
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
EXPECTED_W = 1024
EXPECTED_H = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def load_checked_png(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        raise SystemExit("gate failed: entry.png exceeds 1 MiB")
    if not data.startswith(PNG_SIGNATURE):
        raise SystemExit("gate failed: entry.png is not a PNG")
    if data[12:16] != b"IHDR":
        raise SystemExit("gate failed: missing IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width != EXPECTED_W or height != EXPECTED_H:
        raise SystemExit(
            "gate failed: expected 1024x1024, got %dx%d" % (width, height)
        )
    return data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data = load_checked_png(os.path.join(here, "entry.png"))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
            fh.write(data)
    else:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
