# Decrypt MOSAIC Data

Decrypt a MOSAIC data folder (`.enc` / `.lzma.enc`) next to the original encrypted files.
The main entry point is `decrypt.py`. Use `join_chunks.py` to join chunk files on their own.

## Requirements

- Python **3.9** or **3.11** on macOS (arm64), matching a built `.so` module
- The `cryptography` package

| Python | Compiled module |
| --- | --- |
| 3.9 | `mosaic_decrypt.cpython-39-darwin.so` |
| 3.11 | `mosaic_decrypt.cpython-311-darwin.so` |

## Create a virtual environment

Create the venv with the same Python version you will run.

Python 3.9:

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Python 3.11:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check the active Python version:

```bash
python --version
```

Deactivate the virtual environment when finished:

```bash
deactivate
```

## Input folder layout

Each MOSAIC session should look like this:

```
data/MOSAIC-YYYYMMDD-HHMMSS-XXXX/
  MOSAIC-YYYYMMDD-HHMMSS-XXXX_Harmonized_JSON/
    session_information.json
  <deviceId>_<timestamp>/
    SESSION/                      # look for sync_info here first
      sync_info.json.enc
      # or <tempId>_sync_info.json.enc
      # or sync_info.json.lzma.enc / <tempId>_sync_info.json.lzma.enc
    METRIC/                       # fallback if SESSION/ has no sync_info
      sync_info.json.enc
      # or <tempId>_sync_info.json.enc
      # or sync_info.json.lzma.enc / <tempId>_sync_info.json.lzma.enc
    .../*.lzma.enc
```

If `sync_info.json.enc` (or `<tempId>_sync_info.json.enc`) exists, use the current JSON flow. If only `sync_info.json.lzma.enc` exists, AES-decrypt it first and read `syncUDID`. When that key is empty, decompress the LZMA payload, then read `syncUDID`.

`tempId` is taken from `<tempId>_sync_info.json.enc` or `<tempId>_sync_info.json.lzma.enc`. If the file is only `sync_info.json.enc` / `sync_info.json.lzma.enc`, `tempId` is read from `session_information.json`.

## How to run

Activate the venv (if it is not already active), then pass the session folder:

```bash
source .venv/bin/activate
python decrypt.py data/MOSAIC-YYYYMMDD-HHMMSS-XXXX
```

Example:

```bash
python decrypt.py data/MOSAIC-20260817-024132-8A3A
```

`decrypt.py` decrypts, decompresses, then joins chunk files automatically.

## Copying to another Mac

No extra `codesign` / `xattr` step is required. On first run, `decrypt.py` removes the macOS quarantine flag from the tool folder and ad-hoc-signs `mosaic_decrypt*.so` for that machine.

If System Settings still shows a malware warning, click **Allow**, then run the same command again.

## Join chunk files

After decompress, files named `{timestamp}_{index}` (`_0000` … `_XXXX`) in the same folder are concatenated in index order into `{Folder}_joined`.

Example: `EEG2/1786935419_0000` + `EEG2/1786936319_0001` + `EEG2/1786936453_0002` → `EEG2/EEG2_joined`.

Run join on its own (no decrypt) if the chunks are already decompressed:

```bash
python join_chunks.py data/MOSAIC-YYYYMMDD-HHMMSS-XXXX
```

Or join a single sensor folder:

```bash
python join_chunks.py data/MOSAIC-20260817-024132-8A3A/E244CH43FX1U_1786934519000/EEG2
```

## Output files

Files are written next to the encrypted source:

| Input | After decrypt | After decompress |
| --- | --- | --- |
| `sync_info.json.enc` | `sync_info.json` | — |
| `sync_info.json.lzma.enc` | `sync_info.json.lzma` (only if the AES payload is LZMA) | `sync_info.json` |
| `BETA_SCORE.json.lzma.enc` | `BETA_SCORE.json.lzma` | `BETA_SCORE.json` |
| `1786935419_0000.lzma.enc` | `1786935419_0000.lzma` | `1786935419_0000` |

Original `.enc` files are kept. Intermediate `.lzma` files are also kept.

The decrypted `syncUDID` is used only in memory and is not written to the JSON file.

The `Done: N/N .lzma.enc` line counts only sensor/data `.lzma.enc` files. `sync_info.json.enc` and `sync_info.json.lzma.enc` are decrypted earlier to obtain the key and are **not** included in that count.

## Python source (for edits / rebuild)

Decryption source lives in `src/`, separate from the `decrypt.py` entry point.

Run directly from source:

```bash
source .venv/bin/activate
python src/decrypt_mosaic_folder.py data/MOSAIC-YYYYMMDD-HHMMSS-XXXX
```

Rebuild the `.so` module after editing `src/mosaic_decrypt.py`. Use the same Python version as the target runtime:

```bash
source .venv/bin/activate
python -m pip install cython setuptools
python -c "from setuptools import setup; from Cython.Build import cythonize; import sys; sys.argv = ['setup', 'build_ext', '--inplace']; setup(ext_modules=cythonize('src/mosaic_decrypt.py', language_level=3))"
mv src/mosaic_decrypt*.so ./
rm -f src/mosaic_decrypt.c
```

That produces `mosaic_decrypt.cpython-39-darwin.so` on Python 3.9, or `mosaic_decrypt.cpython-311-darwin.so` on Python 3.11.

On a new Mac, do **not** sign the `.so` by hand. The first `python decrypt.py ...` run clears the quarantine flag (from copy / git clone / Sourcetree) and ad-hoc-signs the module for that machine automatically.

If macOS still shows “Apple could not verify … is free of malware”, click **Allow** in System Settings > Privacy & Security, then run `decrypt.py` again.

## Files in this repo

| File | Role |
| --- | --- |
| `decrypt.py` | Entry point: pass the MOSAIC session folder to decrypt |
| `join_chunks.py` | Join `{timestamp}_{index}` files into `{Folder}_joined` |
| `mosaic_decrypt.cpython-39-darwin.so` | Compiled module for Python 3.9 |
| `mosaic_decrypt.cpython-311-darwin.so` | Compiled module for Python 3.11 |
| `src/` | Python source used for edits or rebuilds |
| `requirements.txt` | Python dependencies |
