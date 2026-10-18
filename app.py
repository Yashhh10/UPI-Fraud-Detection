import streamlit as st
import pandas as pd
import plotly.express as px

def format_indian_rupees(num):
    x = str(int(num))
    if len(x) <= 3:
        return x
    last_three = x[-3:]
    rest = x[:-3]
    rest = ','.join([rest[::-1][i:i+2] for i in range(0, len(rest), 2)])[::-1]
    return rest + ',' + last_three

# 1. Page ki Setting
st.set_page_config(page_title="UPI Fraud Alerts", layout="wide")
st.title("🚨 UPI FRAUD ALERTS SYSTEM")

# 2. Data Load karna
@st.cache_data
def load_data():
    return pd.read_csv('analyzed_upi_data.csv')

df = load_data()

# 3. Slicer (Sidebar Filter)
st.sidebar.header("Filter Transactions")
unique_flags = df['Fraud_Flag'].unique().tolist()
options = ["All"] + unique_flags  
risk_level = st.sidebar.radio("Select Risk Level:", options)

if risk_level != "All":
    filtered_df = df[df['Fraud_Flag'] == risk_level]
else:
    filtered_df = df

# 4. Cards (Top Metrics)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Transactions", value=len(filtered_df))
with col2:
    # Yahan naya Indian format apply kiya gaya hai
    total_amt = format_indian_rupees(filtered_df['Amount'].sum())
    st.metric(label="Total Amount (₹)", value=f"₹ {total_amt}")

# 5. Charts banana
col3, col4 = st.columns(2)

with col3:
    st.subheader("Fraud Categories")
    fig_donut = px.pie(filtered_df, names='Fraud_Flag', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_donut, use_container_width=True)

with col4:
    st.subheader("Hourly Transaction Trend")
    hourly_data = filtered_df.groupby('Hour')['Amount'].sum().reset_index()
    fig_line = px.line(hourly_data, x='Hour', y='Amount', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)
