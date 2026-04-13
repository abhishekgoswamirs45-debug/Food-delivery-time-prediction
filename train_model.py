import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

# Load dataset
data = pd.read_csv("data.csv")

# Features (inputs)
X = data[["distance", "prep_time", "traffic"]]

# Target (output)
y = data["delivery_time"]

# Split data (training + testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create model
model = LinearRegression()

# Train model
model.fit(X_train, y_train)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved successfully ✅")