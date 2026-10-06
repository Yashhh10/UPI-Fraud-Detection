import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ==========================================
# 1. Page ki setting aur Title
# ==========================================
st.set_page_config(page_title="PingP&L Dashboard", layout="wide")
st.title("🚀 PingP&L: Notification Guardrail System")
st.markdown("Find the exact 'Tipping Point' where push notifications start destroying unit economics.")

# ==========================================
# 2. Database se Data lana
# ==========================================
conn = sqlite3.connect('ping_pnl_data.db')
query = """
SELECT 
    notifications_received as Pings,
    COUNT(user_id) as Total_Users,
    SUM(churned) as Churned_Users,
    ROUND((SUM(churned) * 100.0 / COUNT(user_id)), 2) as Churn_Rate_Pct,
    (COUNT(user_id) * notifications_received * 40) as Gross_Revenue,
    (SUM(churned) * 350) as Churn_Loss_CAC,
    ((COUNT(user_id) * notifications_received * 40) - (SUM(churned) * 350)) as Net_PnL
FROM user_metrics
GROUP BY notifications_received
ORDER BY notifications_received;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# ==========================================
# 3. Data aur Graphs ko screen par dikhana
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Raw Data (Unit Economics)")
    st.dataframe(df)

with col2:
    st.markdown("### 📉 Net Profit vs Notification Count")
    fig = px.bar(
        df, 
        x='Pings', 
        y='Net_PnL', 
        title="Green = Profit | Red = Loss (Tipping Point)",
        color='Net_PnL', 
        color_continuous_scale=["red", "green"] 
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 4. AI Operations Directive (GEMINI AI)
# ==========================================
st.markdown("### 🤖 AI Operations Directive")

# 🔥 BAS YAHAN APNI API KEY DAALNI HAI 🔥
API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.8-flash')

prompt = f"""
You are a Chief Business Officer. Look at this notification profit/loss data:
{df[['Pings', 'Net_PnL']].to_string(index=False)}

Write a short, strict 3-line memo to the marketing team. 
Identify the exact notification count where Net_PnL turns negative (the tipping point). 
Order them to set a hard cap on daily notifications to prevent CAC losses.
"""

# Ye button ab pakka dikhega screen par
if st.button("Generate Strategy Memo"):
    if API_KEY == "TUMHARA_API_KEY_YAHAN_PASTE_KARO":
        st.error("⚠️ Bhai, Code me line number 48 par apna asli API Key daalna bhool gaye!")
    else:
        with st.spinner("AI is analyzing unit economics..."):
            try:
                response = model.generate_content(prompt)
                st.success(response.text)
            except Exception as e:
                st.error(f"Error aaya hai bhai: {e}")