"""Required-input validation tests."""

from pathlib import Path

from weavemark.cli_inputs import missing_user_inputs


def test_blank_string_is_missing_but_false_and_zero_are_supplied(tmp_path: Path) -> None:
    spec = "@{ticker} @{include_history} @{limit}"

    missing = missing_user_inputs(
        spec,
        {
            "ticker": "   ",
            "include_history": False,
            "limit": 0,
        },
        tmp_path,
    )

    assert [item.name for item in missing] == ["ticker"]
