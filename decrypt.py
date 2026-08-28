#!/usr/bin/env python3
"""Decrypt a MOSAIC data folder (.enc / .lzma.enc)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from join_chunks import join_chunk_files

SUPPORTED_PYTHON = ((3, 9), (3, 11))
ROOT = Path(__file__).resolve().parent


def _require_supported_python() -> None:
    version = sys.version_info[:2]
    if version in SUPPORTED_PYTHON:
        return
    supported = " or ".join(f"{major}.{minor}" for major, minor in SUPPORTED_PYTHON)
    raise SystemExit(
        f"Unsupported Python {sys.version_info.major}.{sys.version_info.minor}. "
        f"Use Python {supported} on macOS."
    )


def _extension_path() -> Path:
    tag = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
    return ROOT / f"mosaic_decrypt.{tag}-darwin.so"


def _is_gatekeeper_block(error: BaseException) -> bool:
    message = str(error).lower()
    return (
        "disallowed by system policy" in message
        or "code signature" in message
        or "malware" in message
    )


def _trust_local_extension(path: Path) -> None:
    subprocess.run(
        ["xattr", "-d", "com.apple.quarantine", str(path)],
        check=False,
        capture_output=True,
    )
    signed = subprocess.run(
        ["codesign", "--force", "--sign", "-", str(path)],
        capture_output=True,
        text=True,
    )
    if signed.returncode != 0:
        detail = (signed.stderr or signed.stdout).strip()
        raise RuntimeError(detail or "codesign failed")


def _load_decrypt_folder():
    try:
        from mosaic_decrypt import decrypt_folder as loaded
        return loaded
    except ImportError as error:
        so_path = _extension_path()
        if sys.platform == "darwin" and so_path.is_file() and _is_gatekeeper_block(error):
            try:
                _trust_local_extension(so_path)
                from mosaic_decrypt import decrypt_folder as loaded
                return loaded
            except Exception as fix_error:
                raise SystemExit(
                    "macOS blocked mosaic_decrypt because the .so is unsigned or "
                    "quarantined. Allow it in System Settings > Privacy & Security, "
                    f"or run: xattr -d com.apple.quarantine '{so_path}' && "
                    f"codesign --force --sign - '{so_path}'"
                ) from fix_error
        raise SystemExit(
            "Could not import mosaic_decrypt. Install cryptography and use the "
            ".so built for this Python version "
            "(mosaic_decrypt.cpython-39-darwin.so or mosaic_decrypt.cpython-311-darwin.so)."
        ) from error


_require_supported_python()
decrypt_folder = _load_decrypt_folder()


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
