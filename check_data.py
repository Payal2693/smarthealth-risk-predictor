import pandas as pd

# Load heart disease dataset
heart_df = pd.read_csv("datasets/heart-disease.csv")

print("HEART DATASET COLUMNS:")
print(heart_df.columns.tolist())

print("\nFirst 5 rows:")
print(heart_df.head())


# Load diabetes dataset
diabetes_df = pd.read_csv("datasets/diabetes.csv")

print("\nDIABETES DATASET COLUMNS:")
print(diabetes_df.columns.tolist())

print("\nFirst 5 rows:")
print(diabetes_df.head())