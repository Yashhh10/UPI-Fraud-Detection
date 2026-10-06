# 🚨 End-to-End UPI Fraud Detection System

🌐 **Live Dashboard Link:** [https://upi-fraud-detection-2.streamlit.app/]

## 📌 Project Overview
This project simulates a real-time UPI fraud detection and alert system. It analyzes 5,000+ synthetic transactions to identify suspicious activities (like unusually high amounts or odd-hour transactions) and visualizes the insights on an interactive web dashboard.

### ✨ The Final Dashboard:
[<img width="1920" height="1080" alt="Screenshot (24)" src="https://github.com/user-attachments/assets/105a3011-17d5-4966-bdf6-d39d97b4cf2f" />
<img width="1920" height="1080" alt="Screenshot (25)" src="https://github.com/user-attachments/assets/d8d31f06-9b65-4c46-aaf8-5a6e996d3da5" />
<img width="1920" height="1080" alt="Screenshot (26)" src="https://github.com/user-attachments/assets/872e4597-a99d-4620-ba0e-5653acdbb9d5" />
<img width="1920" height="1080" alt="Screenshot (27)" src="https://github.com/user-attachments/assets/d6621dba-7dbb-4d6f-8555-8eebc35deafd" />
]

---

## 🛠️ Tech Stack Used
* **Data Processing & Logic:** Python, Pandas, NumPy
* **Anomaly Detection:** IQR (Interquartile Range) Statistical Logic
* **Data Visualization:** Plotly Express
* **Web App Deployment:** Streamlit

---

## ⚙️ How It Works (The Logic)
1. **Data Generation:** Created a realistic synthetic dataset representing normal banking patterns and injected 5% high-risk fraud patterns.
2. **Rule-Based Engine:** Used the **IQR method** to establish thresholds for transaction amounts. Any amount crossing the upper bound is flagged as an 'Amount Outlier'.
3. **Time-Series Flagging:** Transactions occurring during typical low-volume hours (e.g., 1 AM - 4 AM) are tagged for secondary review.
4. **Interactive BI:** The Streamlit app reads the processed dataset and allows business users to filter data dynamically to monitor risk levels.

---
