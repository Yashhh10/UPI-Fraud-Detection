"""
UPI Fraud Alerts System - Streamlit dashboard
Run:  streamlit run app.py
All money is shown in the Indian numbering system (thousand, lakh, crore).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="UPI Fraud Alerts", page_icon="🚨", layout="wide")

RISK_COLORS = {
    "Safe": "#2E8B57",
    "Medium Risk (Odd Hour)": "#E0A800",
    "High Risk (Amount Outlier)": "#D64545",
}
ODD_HOURS = (0, 4)


# ---------- Indian number formatting ----------
def format_inr(value: float, decimals: int = 0) -> str:
    """89588322.02 -> '₹ 8,95,88,322' (Indian digit grouping)."""
    text = f"{abs(value):.{decimals}f}"
    whole, _, frac = text.partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    sign = "-" if value < 0 else ""
    return f"{sign}₹ {whole}" + (f".{frac}" if frac else "")


def format_inr_short(value: float) -> str:
    """89588322 -> '₹ 8.96 Cr', 262821 -> '₹ 2.63 L'."""
    if abs(value) >= 1e7:
        return f"₹ {value / 1e7:.2f} Cr"
    if abs(value) >= 1e5:
        return f"₹ {value / 1e5:.2f} L"
    return format_inr(value)


def format_count(n: int) -> str:
    return format_inr(n).replace("₹ ", "")


# ---------- Data ----------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("analyzed_upi_data.csv", parse_dates=["Timestamp"])
    if "Risk_Reason" not in df.columns:  # older output of Fraud_detection.py
        df["Risk_Reason"] = df["Fraud_Flag"]
    df["Date"] = df["Timestamp"].dt.date
    df["Month"] = df["Timestamp"].dt.to_period("M").dt.to_timestamp()
    return df


df = load_data()
q1, q3 = df["Amount"].quantile([0.25, 0.75])
threshold = q3 + 1.5 * (q3 - q1)

# ---------- Sidebar filters ----------
st.sidebar.header("Filter transactions")

risk_options = ["All"] + [f for f in RISK_COLORS if f in df["Fraud_Flag"].unique()]
risk_level = st.sidebar.radio("Risk level", risk_options)

cities = sorted(df["Location"].unique())
selected_cities = st.sidebar.multiselect("City", cities, placeholder="All cities")

min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input(
    "Date range", (min_date, max_date), min_value=min_date, max_value=max_date
)

st.sidebar.divider()
st.sidebar.markdown("**Detection rules**")
st.sidebar.markdown(
    f"- Amount above **{format_inr(threshold)}** (Q3 + 1.5 × IQR)\n"
    f"- Time between **12 AM and 4:59 AM**"
)

filtered = df.copy()
if risk_level != "All":
    filtered = filtered[filtered["Fraud_Flag"] == risk_level]
if selected_cities:
    filtered = filtered[filtered["Location"].isin(selected_cities)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered["Date"] >= start) & (filtered["Date"] <= end)]

# ---------- Header ----------
st.title("🚨 UPI Fraud Alerts System")
st.caption(
    f"Rule-based anomaly detection on {format_count(len(df))} UPI transactions "
    f"across {df['Location'].nunique()} cities "
    f"({min_date:%d %b %Y} to {max_date:%d %b %Y})"
)

if filtered.empty:
    st.warning("No transactions match these filters. Widen the date range or clear the city filter.")
    st.stop()

# ---------- KPI cards ----------
flagged = filtered[filtered["Fraud_Flag"] != "Safe"]
total_value = filtered["Amount"].sum()
flagged_value = flagged["Amount"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total transactions", format_count(len(filtered)))
k2.metric("Total value", format_inr_short(total_value), help=format_inr(total_value))
k3.metric(
    "Flagged transactions",
    format_count(len(flagged)),
    f"{len(flagged) / len(filtered):.1%} of transactions",
    delta_color="off",
)
k4.metric(
    "Value at risk",
    format_inr_short(flagged_value),
    f"{flagged_value / total_value:.1%} of total value" if total_value else None,
    delta_color="off",
    help=format_inr(flagged_value),
)

# ---------- Row 1: category split + hourly trend ----------
c1, c2 = st.columns([2, 3])

with c1:
    st.subheader("Risk categories")
    fig_donut = px.pie(
        filtered, names="Fraud_Flag", hole=0.55,
        color="Fraud_Flag", color_discrete_map=RISK_COLORS,
    )
    fig_donut.update_traces(textinfo="percent+value")
    fig_donut.update_layout(legend=dict(orientation="h", y=-0.1), margin=dict(t=10, b=10))
    st.plotly_chart(fig_donut, width="stretch")

with c2:
    st.subheader("Hourly transaction trend")
    hourly = (
        filtered.groupby("Hour")
        .agg(Amount=("Amount", "sum"), Count=("Transaction_ID", "count"))
        .reindex(range(24), fill_value=0)
        .reset_index()
    )
    hourly["Amount_Lakh"] = hourly["Amount"] / 1e5
    hourly["Amount_Text"] = hourly["Amount"].apply(format_inr)
    fig_hour = go.Figure()
    fig_hour.add_vrect(
        x0=ODD_HOURS[0] - 0.5, x1=ODD_HOURS[1] + 0.5,
        fillcolor="#D64545", opacity=0.08, line_width=0,
        annotation_text="Odd hours", annotation_position="top left",
    )
    fig_hour.add_trace(go.Scatter(
        x=hourly["Hour"], y=hourly["Amount_Lakh"], mode="lines+markers",
        customdata=hourly[["Amount_Text", "Count"]],
        hovertemplate="Hour %{x}:00<br>%{customdata[0]}<br>%{customdata[1]} transactions<extra></extra>",
        line=dict(color="#3B5BDB", width=2.5),
    ))
    fig_hour.update_layout(
        xaxis=dict(title="Hour of day", dtick=2),
        yaxis=dict(title="Amount (₹ lakh)"),
        margin=dict(t=10, b=10), showlegend=False,
    )
    st.plotly_chart(fig_hour, width="stretch")

# ---------- Row 2: city + month ----------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Flagged transactions by city")
    by_city = (
        flagged.groupby("Location")
        .agg(Count=("Transaction_ID", "count"), Amount=("Amount", "sum"))
        .sort_values("Count")
        .reset_index()
    )
    if by_city.empty:
        st.info("No flagged transactions for this selection.")
    else:
        by_city["Amount_Text"] = by_city["Amount"].apply(format_inr_short)
        fig_city = px.bar(
            by_city, x="Count", y="Location", orientation="h",
            text="Count", custom_data=["Amount_Text"],
            color_discrete_sequence=["#D64545"],
        )
        fig_city.update_traces(
            hovertemplate="%{y}<br>%{x} flagged<br>%{customdata[0]} at risk<extra></extra>"
        )
        fig_city.update_layout(xaxis_title="Flagged transactions", yaxis_title=None,
                               margin=dict(t=10, b=10))
        st.plotly_chart(fig_city, width="stretch")

with c4:
    st.subheader("Monthly transaction value")
    monthly = (
        filtered.groupby(["Month", "Fraud_Flag"])["Amount"].sum().reset_index()
    )
    monthly["Amount_Lakh"] = monthly["Amount"] / 1e5
    fig_month = px.bar(
        monthly, x="Month", y="Amount_Lakh", color="Fraud_Flag",
        color_discrete_map=RISK_COLORS,
    )
    fig_month.update_layout(
        xaxis=dict(title=None, tickformat="%b"),
        yaxis=dict(title="Amount (₹ lakh)"),
        legend=dict(orientation="h", y=-0.2, title=None),
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig_month, width="stretch")

# ---------- Alert table ----------
st.subheader("Flagged transactions")
if flagged.empty:
    st.info("No flagged transactions for this selection.")
else:
    table = (
        flagged.sort_values("Amount", ascending=False)
        [["Transaction_ID", "Timestamp", "Sender", "Receiver", "Location",
          "Amount", "Fraud_Flag", "Risk_Reason"]]
        .copy()
    )
    display = table.copy()
    display["Amount"] = display["Amount"].apply(lambda v: format_inr(v, 2))
    display["Timestamp"] = display["Timestamp"].dt.strftime("%d %b %Y, %I:%M %p")
    display.columns = ["Transaction ID", "Date & time", "Sender", "Receiver", "City",
                       "Amount", "Risk level", "Reason"]
    st.dataframe(display, width="stretch", hide_index=True, height=360)
    st.download_button(
        "Download flagged transactions (CSV)",
        table.to_csv(index=False).encode("utf-8"),
        file_name="flagged_upi_transactions.csv",
        mime="text/csv",
    )

with st.expander("How the detection works"):
    st.markdown(
        f"""
1. **Amount outlier (IQR):** Q1 = {format_inr(q1)}, Q3 = {format_inr(q3)}.
   Anything above Q3 + 1.5 × IQR = **{format_inr(threshold)}** is flagged as *High Risk*.
2. **Odd hour:** transactions between 12:00 AM and 4:59 AM are flagged as *Medium Risk*
   when the amount is normal.
3. **Risk reason** records every rule that fired, so a large payment at 3 AM shows
   *High amount + Odd hour*.

Rules were chosen over a trained model because the data has no confirmed fraud labels,
and every alert needs a reason an analyst can explain.
"""
    )
