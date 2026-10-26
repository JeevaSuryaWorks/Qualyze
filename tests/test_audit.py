import pandas as pd
import pytest
from datasentinel.audit import audit_dataframe
from datasentinel.cleaning import clean_dataframe

def test_detects_missing_duplicates_constant_and_outlier():
    df = pd.DataFrame({
        "feature": [1, 2, 3, 4, 100, None],
        "constant": ["x"] * 6,
        "target": [0, 0, 0, 1, 1, 0]
    })
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    report = audit_dataframe(df, target="target")
    ids = {f["rule_id"] for f in report["findings"]}
    assert "DQ001" in ids
    assert "DQ002" in ids
    assert "DQ003" in ids
    assert "DQ004" in ids

def test_empty_dataframe_rejected():
    with pytest.raises(ValueError):
        audit_dataframe(pd.DataFrame())

def test_cleaning_logs_actions_and_removes_duplicates():
    df = pd.DataFrame({"x": [1, 1, None], "category": ["a", "a", "b"]})
    cleaned, actions = clean_dataframe(df, drop_duplicates=True, fill_missing=True)
    assert len(cleaned) == 2
    assert cleaned["x"].isna().sum() == 0
    assert actions["output_rows"] == 2

def test_target_leakage_is_warning_not_proof():
    df = pd.DataFrame({"x": list(range(20)), "target": [0, 1] * 10, "target_copy": [0, 1] * 10})
    report = audit_dataframe(df, target="target")
    matches = [f for f in report["findings"] if f["rule_id"] == "ML002"]
    assert matches
    assert "not proof" in matches[0]["recommendation"].lower()
