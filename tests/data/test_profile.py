import json
from io import StringIO
from pathlib import Path

import pandas as pd

from creditsense.data.checksum import write_checksum
from creditsense.data.profile import (
    BLANK_LABEL,
    PROFILE_END,
    PROFILE_START,
    infer_kind,
    main,
    profile_frame,
    render_profile,
    splice_section,
)

RAW_CSV = """LoanNr_ChkDgt,Name,ApprovalDate,ApprovalFY,DisbursementGross,RevLineCr,MIS_Status
1000014003,ACME LLC,28-Feb-97,1997,"$60,000.00 ",N,P I F
1000024006,BETA INC,28-Feb-97,1997,"$40,000.00 ",Y,CHGOFF
1000034009,GAMMA CO,1-Jul-12,2012,"$15,000.00 ",,
1000044001,DELTA CO,3-Mar-76,1976A,"$5,000.00 ",N,P I F
"""


def _frame() -> pd.DataFrame:
    return pd.read_csv(StringIO(RAW_CSV), dtype=str, keep_default_na=False)


def test_infer_kind() -> None:
    assert infer_kind(pd.Series(["1", "22", ""])) == ("integer", 0)
    assert infer_kind(pd.Series(["$1,000.00 ", "$0.00"])) == ("money", 0)
    assert infer_kind(pd.Series(["28-Feb-97", "1-Jul-12"])) == ("date", 0)
    assert infer_kind(pd.Series(["N", "Y"])) == ("text", 0)
    assert infer_kind(pd.Series(["", " "])) == ("empty", 0)


def test_profile_counts() -> None:
    profile = profile_frame(_frame())

    assert profile["rows"] == 4
    assert profile["columns"] == 7
    assert profile["status_counts"] == {"CHGOFF": 1, "P I F": 2, BLANK_LABEL: 1}
    assert profile["non_integer_years"] == ["1976A"]
    assert profile["loans_per_approval_year"]["1997"] == {"CHGOFF": 1, "P I F": 1, BLANK_LABEL: 0}

    by_name = {c["name"]: c for c in profile["column_profiles"]}
    assert by_name["DisbursementGross"]["kind"] == "money"
    assert by_name["ApprovalDate"]["kind"] == "date"
    assert by_name["RevLineCr"]["blank"] == 1
    assert by_name["RevLineCr"]["value_counts"] == {"N": 2, "Y": 1, BLANK_LABEL: 1}


def test_identifying_columns_never_list_values() -> None:
    profile = profile_frame(_frame())
    by_name = {c["name"]: c for c in profile["column_profiles"]}

    assert "value_counts" not in by_name["Name"]
    assert "value_counts" not in by_name["LoanNr_ChkDgt"]


def test_splice_replaces_only_the_section() -> None:
    doc = f"# Data\n\nintro\n\n{PROFILE_START}\nold\n{PROFILE_END}\n\n## Later\n"
    new = splice_section(doc, f"{PROFILE_START}\nnew\n{PROFILE_END}")

    assert "old" not in new
    assert "new" in new
    assert new.startswith("# Data\n\nintro\n")
    assert new.endswith("\n\n## Later\n")


def test_splice_appends_when_markers_missing() -> None:
    new = splice_section("# Data\n", f"{PROFILE_START}\nx\n{PROFILE_END}")
    assert new == f"# Data\n\n{PROFILE_START}\nx\n{PROFILE_END}\n"


def test_main_writes_json_and_doc(tmp_path: Path) -> None:
    raw = tmp_path / "SBAnational.csv"
    raw.write_text(RAW_CSV, encoding="utf-8")
    checksum = tmp_path / "CHECKSUM.txt"
    digest = write_checksum(raw, checksum)
    profile_file = tmp_path / "artifacts" / "profile.json"
    doc = tmp_path / "DATA.md"
    doc.write_text(f"# Data\n\n{PROFILE_START}\n{PROFILE_END}\n", encoding="utf-8")

    args = ["--raw-file", str(raw), "--checksum-file", str(checksum)]
    assert main([*args, "--profile-file", str(profile_file), "--data-doc", str(doc)]) == 0

    profile = json.loads(profile_file.read_text(encoding="utf-8"))
    assert profile["source_sha256"] == digest
    rendered = doc.read_text(encoding="utf-8")
    assert render_profile(profile) in rendered
    assert "- Rows: 4" in rendered
    assert "`1976A`" in rendered


def test_backtick_values_render_as_code() -> None:
    frame = _frame()
    frame.loc[0, "RevLineCr"] = "`"
    profile = profile_frame(frame)
    profile["source_file"] = "SBAnational.csv"
    profile["source_sha256"] = "0" * 64

    assert "`` ` ``: 1" in render_profile(profile)
