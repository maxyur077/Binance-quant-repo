import pandas as pd
import numpy as np

df = pd.read_csv("C:/Users/mayur/OneDrive/Desktop/Azalyst_Live_Trader/backtest_trades_regime-adaptive copy 3.csv")
print("Data Loaded.")
print("Total Trades:", len(df))
print("Columns:", df.columns.tolist())

# Clean PnL $ column
df['PnL $'] = df['PnL $'].str.replace('$', '').str.replace(',', '').astype(float)
df['PnL %'] = df['PnL %'].str.replace('%', '').astype(float) / 100

print(f"\nTotal Realized PnL: ${df['PnL $'].sum():.2f}")
print("Average Trade PnL:", df['PnL $'].mean())
print("Win Rate:", len(df[df['PnL $'] > 0]) / len(df) * 100, "%")

print("\n--- Strategy Breakdown ---")
strat_group = df.groupby('Strategies')['PnL $'].agg(['count', 'sum', 'mean'])
print(strat_group.sort_values(by='sum', ascending=False))

print("\n--- Month Breakdown ---")
df['Entry Time'] = pd.to_datetime(df['Entry Time'])
df['Month'] = df['Entry Time'].dt.to_period('M')
month_group = df.groupby('Month')['PnL $'].agg(['count', 'sum'])
print(month_group)

# Compounding Analysis
print("\n--- Compounding Effect Analysis ---")
balance = 100.0 # Starting balance for backtester
balances = []
for pnl in df['PnL $']:
    balance += pnl
    balances.append(balance)
    
df['Equity'] = balances

import matplotlib.pyplot as plt
plt.figure(figsize=(10,6))
plt.plot(df['Entry Time'], df['Equity'], label="Equity Curve")
plt.title("Backtest Equity Curve")
plt.xlabel("Date")
plt.ylabel("Balance ($)")
plt.savefig("C:/Users/mayur/.gemini/antigravity/brain/476db35a-7817-4ac0-9b8c-4f9dba5fd72b/artifacts/equity_curve.png")
print("\nEquity curve saved.")

