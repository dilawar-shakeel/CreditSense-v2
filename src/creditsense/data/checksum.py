"""Write and verify the SHA-256 checksum of the raw SBA dataset.

The checksum file uses the `sha256sum` format: ``<hex digest>  <file name>``.

Usage:
    uv run python -m creditsense.data.checksum write
    uv run python -m creditsense.data.checksum verify
"""

import argparse
import hashlib
import sys
from pathlib import Path

DEFAULT_RAW_FILE = Path("data") / "raw" / "SBAnational.csv"
DEFAULT_CHECKSUM_FILE = Path("data") / "raw" / "CHECKSUM.txt"
_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum(raw_file: Path, checksum_file: Path) -> str:
    """Compute the raw file's checksum and write it to the checksum file."""
    digest = sha256_file(raw_file)
    checksum_file.write_text(f"{digest}  {raw_file.name}\n", encoding="utf-8", newline="\n")
    return digest


def read_checksum(checksum_file: Path) -> tuple[str, str]:
    """Return (digest, file name) from a checksum file."""
    line = checksum_file.read_text(encoding="utf-8").strip()
    digest, _, name = line.partition("  ")
    if len(digest) != 64 or not name:
        raise ValueError(f"Malformed checksum file: {checksum_file}")
    return digest.lower(), name


def verify_checksum(raw_file: Path, checksum_file: Path) -> bool:
    """Return True if the raw file matches the recorded checksum."""
    expected, name = read_checksum(checksum_file)
    if name != raw_file.name:
        raise ValueError(f"Checksum file is for {name!r}, not {raw_file.name!r}")
    return sha256_file(raw_file) == expected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("command", choices=["write", "verify"])
    parser.add_argument("--raw-file", type=Path, default=DEFAULT_RAW_FILE)
    parser.add_argument("--checksum-file", type=Path, default=DEFAULT_CHECKSUM_FILE)
    args = parser.parse_args(argv)

    raw_file: Path = args.raw_file
    checksum_file: Path = args.checksum_file

    if not raw_file.is_file():
        print(f"Raw file not found: {raw_file}", file=sys.stderr)
        return 1

    if args.command == "write":
        digest = write_checksum(raw_file, checksum_file)
        print(f"Wrote {digest} to {checksum_file}")
        return 0

    if not checksum_file.is_file():
        print(f"Checksum file not found: {checksum_file}", file=sys.stderr)
        return 1
    try:
        ok = verify_checksum(raw_file, checksum_file)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not ok:
        print(f"Checksum mismatch for {raw_file}", file=sys.stderr)
        return 1
    print(f"Checksum OK for {raw_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
