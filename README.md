# Decrypt MOSAIC Data

Decrypt a MOSAIC data folder (`.enc` / `.lzma.enc`) next to the original encrypted files.
The only Python entry point to run is `decrypt.py`.

## Requirements

- Python 3.11 (macOS), matching the Python version used to build the `.so` module
- The `cryptography` package

## Create a virtual environment

The `.so` module is bound to CPython 3.11, so the venv must also be created with Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check that Python 3.11 is active:

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
      # or <userId>_sync_info.json.enc
    METRIC/                       # fallback if SESSION/ has no sync_info
      sync_info.json.enc
      # or <userId>_sync_info.json.enc
    .../*.lzma.enc
```

`userId` is taken from `<userId>_sync_info.json.enc` when that filename is used.
If the file is only `sync_info.json.enc`, `userId` (or `profileId`) is read from `session_information.json`.

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

## Output files

Files are written next to the encrypted source:

| Input | After decrypt | After decompress |
| --- | --- | --- |
| `sync_info.json.enc` | `sync_info.json` | — |
| `BETA_SCORE.json.lzma.enc` | `BETA_SCORE.json.lzma` | `BETA_SCORE.json` |
| `1786935419_0000.lzma.enc` | `1786935419_0000.lzma` | `1786935419_0000` |

Original `.enc` files are kept. Intermediate `.lzma` files are also kept.

The decrypted `syncUDID` is used only in memory and is not written to the JSON file.

## Python source (for edits / rebuild)

Decryption source lives in `src/`, separate from the `decrypt.py` entry point.

Run directly from source:

```bash
source .venv/bin/activate
python src/decrypt_mosaic_folder.py data/MOSAIC-YYYYMMDD-HHMMSS-XXXX
```

Rebuild the `.so` module after editing `src/mosaic_decrypt.py`:

```bash
source .venv/bin/activate
python -m pip install cython
cythonize -3 -i src/mosaic_decrypt.py
mv src/mosaic_decrypt*.so ./mosaic_decrypt.cpython-311-darwin.so
rm -f src/mosaic_decrypt.c
```

## Files in this repo

| File | Role |
| --- | --- |
| `decrypt.py` | Entry point: pass the MOSAIC session folder to decrypt |
| `mosaic_decrypt*.so` | Compiled decryption module |
| `src/` | Python source used for edits or rebuilds |
| `requirements.txt` | Python dependencies |
