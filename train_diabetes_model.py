import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the diabetes dataset
df = pd.read_csv("datasets/diabetes.csv")

# Columns where 0 represents invalid or missing values
columns_to_clean = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI"
]

# Replace invalid 0 values with NaN
df[columns_to_clean] = df[columns_to_clean].replace(0, np.nan)

# Fill missing values using median
df[columns_to_clean] = df[columns_to_clean].fillna(
    df[columns_to_clean].median()
)

# Separate input features and target
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Create the model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Diabetes Model Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the trained model
joblib.dump(model, "models/diabetes_model.pkl")

print("\nDiabetes model saved successfully!")