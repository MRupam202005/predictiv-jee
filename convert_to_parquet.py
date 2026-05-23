import pandas as pd
import os

csv_path = os.path.join('data', 'raw', 'merged_jee_cutoff_2018_2025.csv')
parquet_path = os.path.join('data', 'raw', 'merged_jee_cutoff_2018_2025.parquet')

print(f"Loading CSV from {csv_path}...")
df = pd.read_csv(csv_path)

print(f"Saving Parquet to {parquet_path}...")
df.to_parquet(parquet_path, engine='pyarrow')

print("Conversion complete!")
