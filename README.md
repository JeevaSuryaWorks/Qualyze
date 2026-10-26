# DataSentinel — Autonomous Dataset Quality Engineer

DataSentinel is a Python-first academic prototype that profiles tabular datasets, flags data-quality and ML-readiness risks, explains findings, and supports a reproducible cleaning workflow.

## MVP features

- CSV upload and demonstration dataset
- Column profile: inferred type, missing count/rate, unique values and constant-column detection
- Exact duplicate detection
- Numeric IQR outlier screening
- Optional target-aware class imbalance and strong feature-target association screening
- Severity-ranked findings with explanations and recommendations
- Selectable conservative cleaning operations with a JSON action log
- Interactive Streamlit dashboard and Plotly charts
- HTML audit report, JSON findings, cleaned CSV exports
- SQLite audit history
- Pytest unit tests and Dockerfile

## Research and novelty note

DataSentinel is an integration and decision-support prototype, not a claim that dataset profiling is a new research field. Existing systems include Great Expectations, Evidently, whylogs, Cleanlab, and IBM's Data Quality Toolkit. A defensible research contribution should be established through a focused literature review and reproducible experiments.

Potential project study: compare rule-based checks with an ML-readiness workflow on multiple datasets, measuring detection precision/recall for injected known issues, runtime, and usefulness of recommendations. Separate synthetic injected issues from real-world findings.

## Important limitations

- A high feature-target association is only a review signal; it does not prove target leakage.
- IQR outliers may be valid rare cases and are never automatically deleted.
- The quality score is a transparent heuristic, not a universal certification.
- Missing-value imputation may be inappropriate for some domains and should be selected based on data semantics.
- This MVP supports CSV and tabular data, not image, audio, or distributed big-data datasets.

## Requirements

Python 3.11+ and pip.

## Run on Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_sample_data.py
pytest -q
streamlit run app.py
```

## Run on macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python generate_sample_data.py
pytest -q
streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Docker

```bash
docker build -t datasentinel .
docker run --rm -p 8501:8501 datasentinel
```

## Input format

Upload a CSV file. The target column is optional; if provided and present in the dataset, DataSentinel performs additional target-related checks. The included sample file uses `churn` as its target.

## Project structure

```text
datasentinel/
├── app.py
├── generate_sample_data.py
├── requirements.txt
├── Dockerfile
├── README.md
├── data/
│   └── sample_customers.csv
├── datasentinel/
│   ├── __init__.py
│   ├── audit.py
│   ├── cleaning.py
│   ├── reporting.py
│   └── storage.py
└── tests/
    └── test_audit.py
```
