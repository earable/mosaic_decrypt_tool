#!/usr/bin/env python3
"""Join decompressed MOSAIC chunk files `{timestamp}_{index}` into `{Folder}_joined`."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

CHUNK_NAME = re.compile(r"^.+_(\d{4})$")
SKIP_SUFFIXES = {".enc", ".lzma", ".json"}


def is_chunk_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    if path.name.endswith("_joined"):
        return False
    return CHUNK_NAME.match(path.name) is not None


def chunk_index(path: Path) -> int:
    match = CHUNK_NAME.match(path.name)
    if match is None:
        raise ValueError(f"Not a chunk file: {path}")
    return int(match.group(1))


def join_folder_chunks(folder: Path) -> Path | None:
    chunks = [path for path in folder.iterdir() if is_chunk_file(path)]
    if not chunks:
        return None

    chunks.sort(key=lambda path: (chunk_index(path), path.name))
    output_path = folder / f"{folder.name}_joined"
    with output_path.open("wb") as dest:
        for chunk in chunks:
            with chunk.open("rb") as src:
                shutil.copyfileobj(src, dest)
    return output_path


def join_chunk_files(root: Path) -> list[Path]:
    folders = sorted(
        {path.parent for path in root.rglob("*") if is_chunk_file(path)}
    )
    written: list[Path] = []
    for folder in folders:
        output_path = join_folder_chunks(folder)
        if output_path is None:
            continue
        written.append(output_path)
        print(f"Joined: {output_path}")
    return written


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Join {timestamp}_{index} chunk files into {Folder}_joined."
    )
    parser.add_argument("folder", help="MOSAIC session folder (or a sensor subfolder)")
    args = parser.parse_args()
    root = Path(args.folder).resolve()
    if not root.is_dir():
        parser.error(f"Folder not found: {root}")
    written = join_chunk_files(root)
    if not written:
        print(f"No chunk files found in {root}")


if __name__ == "__main__":
    main()
