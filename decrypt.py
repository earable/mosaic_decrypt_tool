#!/usr/bin/env python3
"""Decrypt a MOSAIC data folder (.enc / .lzma.enc)."""

from __future__ import annotations

import argparse
from pathlib import Path

from mosaic_decrypt import decrypt_folder


def main() -> None:
    parser = argparse.ArgumentParser(description="Decrypt a MOSAIC data folder.")
    parser.add_argument("folder", help="Path to the MOSAIC session folder")
    args = parser.parse_args()

    try:
        decrypt_folder(Path(args.folder).resolve())
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
