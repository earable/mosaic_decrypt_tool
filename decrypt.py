#!/usr/bin/env python3
"""Decrypt a MOSAIC data folder (.enc / .lzma.enc)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUPPORTED_PYTHON = ((3, 9), (3, 11))


def _require_supported_python() -> None:
    version = sys.version_info[:2]
    if version in SUPPORTED_PYTHON:
        return
    supported = " or ".join(f"{major}.{minor}" for major, minor in SUPPORTED_PYTHON)
    raise SystemExit(
        f"Unsupported Python {sys.version_info.major}.{sys.version_info.minor}. "
        f"Use Python {supported} on macOS."
    )


_require_supported_python()

try:
    from mosaic_decrypt import decrypt_folder
except ImportError as error:
    raise SystemExit(
        "Could not import mosaic_decrypt. Install cryptography and use the "
        ".so built for this Python version "
        "(mosaic_decrypt.cpython-39-darwin.so or mosaic_decrypt.cpython-311-darwin.so)."
    ) from error

from join_chunks import join_chunk_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Decrypt a MOSAIC data folder.")
    parser.add_argument("folder", help="Path to the MOSAIC session folder")
    args = parser.parse_args()

    try:
        decrypt_folder(Path(args.folder).resolve())
        join_chunk_files(Path(args.folder).resolve())
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
