from pathlib import Path
import numpy as np
import pandas as pd

def create_sample(path="data/sample_customers.csv", seed=42):
    rng = np.random.default_rng(seed)
    n = 500
    age = rng.integers(18, 75, n).astype(float)
    tenure = rng.integers(0, 72, n).astype(float)
    monthly_spend = np.round(rng.normal(1200, 380, n).clip(100, 3000), 2)
    support_calls = rng.poisson(1.4, n).astype(float)
    contract = rng.choice(["monthly", "annual", "two_year"], n, p=[.55, .3, .15]).astype(object)
    churn_probability = 1 / (1 + np.exp(-(-2.2 + .8*(contract=="monthly") + .45*support_calls - .012*tenure)))
    churn = (rng.random(n) < churn_probability).astype(int)
    df = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(n)],
        "age": age, "tenure_months": tenure, "monthly_spend": monthly_spend,
        "support_calls": support_calls, "contract_type": contract,
        "churn": churn
    })
    # Add intentional quality issues for the demo.
    df.loc[[4, 22, 77], "age"] = np.nan
    df.loc[[12, 31], "contract_type"] = None
    df.loc[50, "monthly_spend"] = 12000  # possible outlier
    df.loc[61, "age"] = 250             # suspicious value
    df["constant_export_flag"] = "exported"
    df = pd.concat([df, df.iloc[[8, 8]]], ignore_index=True)
    # High target association column to demonstrate a review-only leakage warning.
    df["churn_copy"] = df["churn"]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Created sample dataset: {path} ({len(df)} rows)")
if __name__ == "__main__":
    create_sample()
