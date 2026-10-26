import numpy as np
import pandas as pd

def _type_name(series):
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "categorical/text"

def _finding(rule_id, severity, title, affected, description, impact, recommendation):
    return {
        "rule_id": rule_id, "severity": severity, "title": title,
        "affected": int(affected), "description": description,
        "impact": impact, "recommendation": recommendation
    }

def audit_dataframe(df: pd.DataFrame, target=None):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("The dataset has no rows.")
    if len(df.columns) == 0:
        raise ValueError("The dataset has no columns.")
    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names found. Rename columns so each name is unique.")

    findings = []
    nrows, ncols = df.shape
    profiles = []
    duplicate_rows = int(df.duplicated().sum())
    if duplicate_rows:
        findings.append(_finding(
            "DQ001", "Medium", "Exact duplicate rows", duplicate_rows,
            f"{duplicate_rows} rows duplicate an earlier row across all columns.",
            "Duplicates can bias statistics and may cause train/test contamination if copies cross dataset splits.",
            "Review whether duplicates are legitimate repeated events; remove exact duplicates only when appropriate."
        ))

    missing_total = int(df.isna().sum().sum())
    if missing_total:
        affected_cols = int((df.isna().sum() > 0).sum())
        findings.append(_finding(
            "DQ002", "Medium", "Missing values", missing_total,
            f"{missing_total} missing cells across {affected_cols} columns.",
            "Missingness may bias analysis or cause model pipelines to fail.",
            "Investigate why values are missing. Compare row removal, imputation, and missingness indicators."
        ))

    for col in df.columns:
        s = df[col]
        missing = int(s.isna().sum())
        unique = int(s.nunique(dropna=True))
        profiles.append({
            "column": str(col),
            "inferred_type": _type_name(s),
            "missing_count": missing,
            "missing_pct": round(100 * missing / max(nrows, 1), 2),
            "unique_values": unique,
            "unique_pct": round(100 * unique / max(nrows, 1), 2),
            "constant": bool(unique <= 1),
        })
        if unique <= 1:
            findings.append(_finding(
                "DQ003", "Low", f"Constant column: {col}", 1,
                f"Column '{col}' has {unique} distinct non-missing value(s).",
                "A constant feature generally provides little predictive information and can indicate a broken extraction.",
                "Verify the source. Drop the column if the constant value is expected and irrelevant."
            ))

    profile_df = pd.DataFrame(profiles)
    # Numeric outlier scan uses IQR fences as a review heuristic, not an automatic deletion rule.
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        s = df[col].replace([np.inf, -np.inf], np.nan).dropna()
        if len(s) < 4 or s.nunique() < 3:
            continue
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
        count = int(mask.fillna(False).sum())
        if count:
            findings.append(_finding(
                "DQ004", "Low", f"Potential outliers: {col}", count,
                f"{count} values fall outside the 1.5×IQR fences for '{col}'.",
                "Extreme values may be valid rare events, measurement errors, or encoding mistakes.",
                "Inspect rows and domain constraints before transforming or removing values."
            ))

    if target and target in df.columns:
        target_s = df[target]
        if target_s.nunique(dropna=True) > 1:
            counts = target_s.value_counts(dropna=False)
            smallest_share = float(counts.min() / max(counts.sum(), 1))
            if smallest_share < 0.10:
                findings.append(_finding(
                    "ML001", "Medium", "Potential target class imbalance", int(counts.min()),
                    f"The least frequent target category represents {smallest_share:.1%} of target observations.",
                    "Accuracy may hide poor minority-class performance.",
                    "Use stratified splits when appropriate and report per-class precision, recall, F1, and a confusion matrix."
                ))
            # High feature-target association is a review signal only; it does not prove leakage.
            for col in df.columns:
                if col == target or df[col].nunique(dropna=True) <= 1:
                    continue
                score = None
                try:
                    if pd.api.types.is_numeric_dtype(df[col]) and pd.api.types.is_numeric_dtype(target_s):
                        pair = df[[col, target]].dropna()
                        if len(pair) >= 10 and pair[col].nunique() > 1 and pair[target].nunique() > 1:
                            score = abs(float(pair[col].corr(pair[target])))
                    elif df[col].nunique(dropna=True) <= 30 and target_s.nunique(dropna=True) <= 20:
                        # Cramér's V-like association estimate from chi-square statistic.
                        import scipy.stats as stats
                        table = pd.crosstab(df[col], target_s)
                        if table.shape[0] > 1 and table.shape[1] > 1:
                            chi2 = stats.chi2_contingency(table, correction=False)[0]
                            n = table.to_numpy().sum()
                            denom = max(min(table.shape[0]-1, table.shape[1]-1), 1)
                            score = float(np.sqrt(chi2 / max(n * denom, 1)))
                except Exception:
                    score = None
                if score is not None and np.isfinite(score) and score >= 0.98:
                    findings.append(_finding(
                        "ML002", "High", f"Review possible target leakage: {col}", 1,
                        f"Feature '{col}' has a very strong observed association with target '{target}' (screening score {score:.3f}).",
                        "A feature derived from the target or unavailable at prediction time can inflate validation scores.",
                        "Check feature provenance and availability time. Test with a time-aware or group-aware split. Association alone is not proof of leakage."
                    ))

    # Quality score is deliberately transparent and heuristic.
    penalty = 0
    for f in findings:
        weight = {"High": 8, "Medium": 4, "Low": 1}.get(f["severity"], 1)
        penalty += weight * max(1, min(f["affected"], 10))
    quality_score = max(0, min(100, 100 - penalty))
    summary = {
        "rows": int(nrows), "columns": int(ncols),
        "duplicate_rows": duplicate_rows, "missing_cells": missing_total,
        "finding_count": len(findings), "quality_score": int(quality_score),
        "target_column": target if target in df.columns else None
    }
    findings.sort(key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}[x["severity"]], x["rule_id"], x["title"]))
    return {"summary": summary, "column_profile": profile_df, "findings": findings}
