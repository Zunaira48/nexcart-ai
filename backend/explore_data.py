import pandas as pd

df = pd.read_csv("data/flipkart_com-ecommerce_sample.csv")

print("Shape (rows, columns):", df.shape)
print()
print("Columns:", df.columns.tolist())
print()
print("First 5 rows:")
print(df.head())
print()
print("Missing values per column:")
print(df.isnull().sum())