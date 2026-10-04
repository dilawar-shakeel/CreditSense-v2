from pathlib import Path

import pytest

from creditsense.data.checksum import main, read_checksum, verify_checksum, write_checksum


@pytest.fixture
def raw_file(tmp_path: Path) -> Path:
    path = tmp_path / "SBAnational.csv"
    path.write_text("LoanNr_ChkDgt,MIS_Status\n1,P I F\n", encoding="utf-8")
    return path


def test_write_then_verify(raw_file: Path, tmp_path: Path) -> None:
    checksum_file = tmp_path / "CHECKSUM.txt"
    digest = write_checksum(raw_file, checksum_file)

    assert read_checksum(checksum_file) == (digest, "SBAnational.csv")
    assert verify_checksum(raw_file, checksum_file)


def test_changed_file_fails(raw_file: Path, tmp_path: Path) -> None:
    checksum_file = tmp_path / "CHECKSUM.txt"
    write_checksum(raw_file, checksum_file)
    raw_file.write_text("tampered\n", encoding="utf-8")

    assert not verify_checksum(raw_file, checksum_file)


def test_wrong_file_name_raises(raw_file: Path, tmp_path: Path) -> None:
    checksum_file = tmp_path / "CHECKSUM.txt"
    checksum_file.write_text(f"{'0' * 64}  other.csv\n", encoding="utf-8")

    with pytest.raises(ValueError, match="other.csv"):
        verify_checksum(raw_file, checksum_file)


def test_cli_exit_codes(raw_file: Path, tmp_path: Path) -> None:
    checksum_file = tmp_path / "CHECKSUM.txt"
    args = ["--raw-file", str(raw_file), "--checksum-file", str(checksum_file)]

    assert main(["verify", *args]) == 1  # no checksum file yet
    assert main(["write", *args]) == 0
    assert main(["verify", *args]) == 0
    raw_file.write_text("tampered\n", encoding="utf-8")
    assert main(["verify", *args]) == 1


def test_cli_missing_raw_file(tmp_path: Path) -> None:
    args = ["--raw-file", str(tmp_path / "missing.csv")]
    assert main(["verify", *args]) == 1
