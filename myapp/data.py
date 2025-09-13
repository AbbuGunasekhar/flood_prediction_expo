import pandas as pd
import numpy as np
import random

# Number of rows
n_rows = 1200  # you can change to 1000, 1500, etc.

# Generate synthetic dataset
data = {
    "current_level": np.round(np.random.uniform(30, 100, n_rows), 2),
    "max_level": np.repeat(100, n_rows),
    "inflow": np.round(np.random.uniform(5, 30, n_rows), 2),
    "outflow": np.round(np.random.uniform(1, 20, n_rows), 2),
    "temperature": np.round(np.random.uniform(20, 40, n_rows), 1),
    "humidity": np.random.randint(40, 100, n_rows),
    "cloud_condition": np.random.choice(
        ["Clear", "Partly Cloudy", "Overcast", "Rainy", "Stormy"], n_rows
    ),
    "last_1hr_rain": np.round(np.random.uniform(0, 50, n_rows), 1),
    "last_3hr_rain": np.round(np.random.uniform(0, 120, n_rows), 1),
    "dam_height": np.round(np.random.uniform(50, 200, n_rows), 1),
    "storage_capacity": np.round(np.random.uniform(100, 500, n_rows), 1),
    "spillway_capacity": np.round(np.random.uniform(50, 300, n_rows), 1),
    "gate_condition": np.random.choice([0, 1, 2], n_rows),  # 0 = poor, 1 = fair, 2 = good
    "released": np.random.choice([0, 1], n_rows),
}

df = pd.DataFrame(data)

# Risk level and time-to-flood calculation
risk_levels = []
time_to_flood = []

for i in range(n_rows):
    wl_ratio = df.loc[i, "current_level"] / df.loc[i, "max_level"]
    rain = df.loc[i, "last_3hr_rain"]

    risk = "Less"
    time_str = np.nan

    if wl_ratio < 0.6 and rain < 30:
        risk = "Less"
    elif wl_ratio < 0.75 and rain < 50:
        risk = "Moderate"
    elif wl_ratio < 0.85 and rain < 80:
        risk = "Risk"
    elif wl_ratio < 0.95 or rain < 100:
        risk = "High Risk"
        days = random.choice([1, 2, 3, 5, 7, 10])
        hours = random.randint(1, 24)
        time_str = f"{days} days {hours} hours"
    else:
        risk = "Severe"
        days = random.choice([1, 2, 3])
        hours = random.randint(1, 12)
        time_str = f"{days} days {hours} hours"

    risk_levels.append(risk)
    time_to_flood.append(time_str)

df["risk_level"] = risk_levels
df["time_to_flood"] = time_to_flood

# Save CSV
df.to_csv("flood_dataset_final.csv", index=False)

print("✅ Dataset generated: flood_dataset_final.csv")
print(df.head(10))
