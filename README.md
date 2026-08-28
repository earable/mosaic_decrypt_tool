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
      # or <xxxx>_sync_info.json.enc
    METRIC/                       # fallback if SESSION/ has no sync_info
      sync_info.json.enc
      # or <xxxx>_sync_info.json.enc
    .../*.lzma.enc
```

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

Rebuild the `.so` module after editing `src/mosaic_decrypt.py`. Use the same Python version as the target runtime:

```bash
source .venv/bin/activate
python -m pip install cython setuptools
python -c "from setuptools import setup; from Cython.Build import cythonize; import sys; sys.argv = ['setup', 'build_ext', '--inplace']; setup(ext_modules=cythonize('src/mosaic_decrypt.py', language_level=3))"
mv src/mosaic_decrypt*.so ./
rm -f src/mosaic_decrypt.c
codesign --force --sign - mosaic_decrypt.cpython-*-darwin.so
xattr -d com.apple.quarantine mosaic_decrypt.cpython-*-darwin.so 2>/dev/null || true
```

That produces `mosaic_decrypt.cpython-39-darwin.so` on Python 3.9, or `mosaic_decrypt.cpython-311-darwin.so` on Python 3.11.

If macOS shows “Apple could not verify … is free of malware”, the `.so` was downloaded or cloned with a quarantine flag (for example via Sourcetree). `decrypt.py` clears that automatically on first run. To fix it by hand:

```bash
xattr -d com.apple.quarantine mosaic_decrypt.cpython-*-darwin.so
codesign --force --sign - mosaic_decrypt.cpython-*-darwin.so
```

## Files in this repo

| File | Role |
| --- | --- |
| `decrypt.py` | Entry point: pass the MOSAIC session folder to decrypt |
| `join_chunks.py` | Join `{timestamp}_{index}` files into `{Folder}_joined` |
| `mosaic_decrypt.cpython-39-darwin.so` | Compiled module for Python 3.9 |
| `mosaic_decrypt.cpython-311-darwin.so` | Compiled module for Python 3.11 |
| `src/` | Python source used for edits or rebuilds |
| `requirements.txt` | Python dependencies |
