import pandas as pd

print("Data load ho raha hai...")
# 1. Apna dataset load karna
df = pd.read_csv('upi_data.csv')

# 2. Data ko theek karna (Time aur Amount ko samajhna)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Hour'] = df['Timestamp'].dt.hour
df['Amount'] = pd.to_numeric(df['Amount'])

# 3. IQR Logic (Jaisa article mein tha) - Bahut zyada amount pakadne ke liye
Q1 = df['Amount'].quantile(0.25)
Q3 = df['Amount'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + (1.5 * IQR)

# 4. Rules banana (Fraud Flag lagana)
def check_fraud(row):
    if row['Amount'] > upper_bound:
        return "High Risk (Amount Outlier)"
    elif row['Hour'] >= 2 and row['Hour'] <= 4:
        return "Medium Risk (Odd Hour)"
    else:
        return "Safe"

# Har row par rules apply karna
print("Rules apply ho rahe hain...")
df['Fraud_Flag'] = df.apply(check_fraud, axis=1)

# 5. Result ko nayi file mein save karna
df.to_csv('analyzed_upi_data.csv', index=False)
print("Badhai ho! Analysis complete. 'analyzed_upi_data.csv' naam ki nayi file ban gayi hai.")