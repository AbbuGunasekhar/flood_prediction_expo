import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

np.random.seed(42)

X = []
y = []

for _ in range(500):
    max_level = 100  # Max water level of dam (m)
    current_level = np.random.uniform(20, 100)   # Current water level
    reservoir_percent = (current_level / max_level) * 100  # % full
    inflow = np.random.uniform(50, 2000)         # Inflow in m³/s
    outflow = np.random.uniform(50, 2500)        # Outflow in m³/s
    rainfall_3h = np.random.uniform(0, 200)      # Rainfall in last 3 hours

    # Flood index considers reservoir percent more strongly
    flood_index = (reservoir_percent * 0.5) + (inflow * 0.0015) + (outflow * 0.001) + (rainfall_3h * 0.4)

    # Assign labels
    if flood_index < 50:
        label = 0  # Low risk
    elif flood_index < 70:
        label = 1  # Moderate risk
    elif flood_index < 90:
        label = 2  # High risk
    else:
        label = 3  # Severe risk

    X.append([current_level, max_level, inflow, outflow, rainfall_3h])
    y.append(label)

X = np.array(X)
y = np.array(y)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'flood_model_reservoir.pkl')

# Check training accuracy
#print(f"Training accuracy: {model.score(X, y)*100:.2f}%")
