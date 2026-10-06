# UPI Fraud Detection System 🚨

## Overview
This project simulates a real-time UPI fraud detection system. It analyzes 5,000+ synthetic UPI transactions to identify suspicious activities using statistical methods and time-series analysis.

## Workflow
1. **Data Generation:** Created a dataset simulating normal and fraudulent UPI transactions (odd hours, unusually high amounts).
2. **Data Analysis (Python):** Used Pandas to process the data and applied the IQR (Interquartile Range) method to flag outliers and high-risk transactions.
3. **Dashboard (Power BI):** Built an interactive dashboard to visualize safe vs. risky transactions, filtering by time and threat level.

## Files in this Repository
* `fraud_detection.py`: The Python script containing the logic for anomaly detection.
* `upi_data.csv`: The raw synthetic dataset.
* `analyzed_upi_data.csv`: The processed dataset with 'Fraud_Flag' column.
* `power BI.pbix`: The interactive Power BI dashboard.
