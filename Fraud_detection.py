"""
UPI Fraud Detection - rule-based anomaly flagging
-------------------------------------------------
Reads raw UPI transactions (upi_data.csv), applies two explainable rules,
and writes analyzed_upi_data.csv, which feeds the Streamlit app and Power BI.

Rule 1 - Amount outlier (IQR method):
    Any amount above Q3 + 1.5 x IQR is treated as unusually large.
Rule 2 - Odd hour:
    Transactions between 12:00 AM and 4:59 AM, when genuine activity is low.

Fraud_Flag (unchanged from v1, so existing dashboards keep working):
    High Risk (Amount Outlier) -> rule 1 fires (with or without rule 2)
    Medium Risk (Odd Hour)     -> only rule 2 fires
    Safe                       -> neither rule fires

New in v2: Risk_Score (0-2) and Risk_Reason record *every* rule that fired,
so a high-value transaction at 3 AM is no longer reported as "amount only".
"""

import pandas as pd

INPUT_FILE = "upi_data.csv"
OUTPUT_FILE = "analyzed_upi_data.csv"
ODD_HOUR_START, ODD_HOUR_END = 0, 4      # 12:00 AM to 4:59 AM
IQR_MULTIPLIER = 1.5


def format_inr(value: float) -> str:
    """Format a number in the Indian system: 89588322 -> '8,95,88,322'."""
    whole = f"{abs(value):.0f}"
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return ("-" if value < 0 else "") + whole


print("Loading data...")
df = pd.read_csv(INPUT_FILE)

# 1. Clean and prepare
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Amount"]).drop_duplicates(subset="Transaction_ID")
df["Hour"] = df["Timestamp"].dt.hour

# 2. IQR threshold for amount outliers
q1, q3 = df["Amount"].quantile([0.25, 0.75])
upper_bound = q3 + IQR_MULTIPLIER * (q3 - q1)

# 3. Evaluate each rule separately (vectorised, no row-by-row apply)
is_outlier = df["Amount"] > upper_bound
is_odd_hour = df["Hour"].between(ODD_HOUR_START, ODD_HOUR_END)

df["Fraud_Flag"] = "Safe"
df.loc[is_odd_hour, "Fraud_Flag"] = "Medium Risk (Odd Hour)"
df.loc[is_outlier, "Fraud_Flag"] = "High Risk (Amount Outlier)"

df["Risk_Score"] = is_outlier.astype(int) + is_odd_hour.astype(int)
df["Risk_Reason"] = "No rule triggered"
df.loc[is_odd_hour & ~is_outlier, "Risk_Reason"] = "Odd hour"
df.loc[is_outlier & ~is_odd_hour, "Risk_Reason"] = "High amount"
df.loc[is_outlier & is_odd_hour, "Risk_Reason"] = "High amount + Odd hour"

# New columns are appended at the end so the Power BI model is not disturbed
df.to_csv(OUTPUT_FILE, index=False)

# 4. Summary
flagged = df[df["Fraud_Flag"] != "Safe"]
print(f"Amount threshold (Q3 + 1.5 x IQR): Rs {format_inr(upper_bound)}")
print(df["Fraud_Flag"].value_counts().to_string())
print(f"Flagged: {len(flagged):,} of {len(df):,} transactions "
      f"({len(flagged) / len(df):.1%})")
print(f"Value at risk: Rs {format_inr(flagged['Amount'].sum())} "
      f"of Rs {format_inr(df['Amount'].sum())} "
      f"({flagged['Amount'].sum() / df['Amount'].sum():.1%})")
print(f"Done. Results saved to {OUTPUT_FILE}")
