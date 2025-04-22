import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/federal_layoff_signal.csv")
df.columns = df.columns.str.strip().str.lower()

df['date'] = pd.to_datetime(df['date'], dayfirst=True)
df['estimated_layoff'] = pd.to_numeric(df['estimated_layoff'], errors='coerce')

monthly = df.groupby(df['date'].dt.to_period("M"))['estimated_layoff'].sum().reset_index()
monthly['date'] = monthly['date'].astype(str)

plt.figure(figsize=(10, 4))
plt.plot(monthly['date'], monthly['estimated_layoff'], marker='o')
plt.xticks(rotation=45)
plt.title('📉 Estimated Layoffs Over Time')
plt.ylabel('Estimated Layoffs')
plt.tight_layout()
plt.savefig("data/layoff_trend_plot.png")
