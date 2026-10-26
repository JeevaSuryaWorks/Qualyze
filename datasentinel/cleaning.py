import pandas as pd

def clean_dataframe(df, drop_duplicates=True, fill_missing=False, drop_empty=False, drop_constant=False):
    cleaned = df.copy()
    actions = {"input_rows": int(len(df)), "input_columns": int(len(df.columns)), "steps": []}

    if drop_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates().copy()
        actions["steps"].append({"action": "drop_exact_duplicates", "rows_removed": int(before-len(cleaned))})

    if drop_empty:
        cols = [c for c in cleaned.columns if cleaned[c].isna().all()]
        cleaned = cleaned.drop(columns=cols)
        actions["steps"].append({"action": "drop_all_empty_columns", "columns_removed": cols})

    if drop_constant:
        cols = [c for c in cleaned.columns if cleaned[c].nunique(dropna=True) <= 1]
        cleaned = cleaned.drop(columns=cols)
        actions["steps"].append({"action": "drop_constant_columns", "columns_removed": cols})

    if fill_missing:
        filled = {}
        for col in cleaned.columns:
            count = int(cleaned[col].isna().sum())
            if count == 0:
                continue
            s = cleaned[col]
            if pd.api.types.is_numeric_dtype(s):
                value = s.median()
                if pd.isna(value):
                    continue
                cleaned[col] = s.fillna(value)
                filled[str(col)] = {"method": "median", "filled": count, "value": float(value)}
            else:
                modes = s.mode(dropna=True)
                if len(modes):
                    value = modes.iloc[0]
                    cleaned[col] = s.fillna(value)
                    filled[str(col)] = {"method": "mode", "filled": count, "value": str(value)}
        actions["steps"].append({"action": "fill_missing", "columns": filled})

    actions["output_rows"] = int(len(cleaned))
    actions["output_columns"] = int(len(cleaned.columns))
    return cleaned, actions
