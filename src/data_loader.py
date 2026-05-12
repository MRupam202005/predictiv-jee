import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
import os

class DataLoader:
    """
    A class to handle the loading and initial inspection of the raw JoSAA dataset.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def load_data(self) -> pd.DataFrame:
        """Loads the raw CSV into a pandas DataFrame."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Data file not found at: {self.file_path}")
        
        print(f"Loading data from {self.file_path}...")
        # We use low_memory=False because some columns might have mixed types initially (e.g., '1234' vs '1234P')
        self.df = pd.read_csv(self.file_path, low_memory=False)
        print(f"Data successfully loaded. Shape: {self.df.shape} (Rows, Columns)\n")
        return self.df

    def inspect_data(self):
        """Performs initial EDA (Exploratory Data Analysis) to check for missing values and inconsistencies."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("-" * 40)
        print("1. DATA TYPES & MISSING VALUES")
        print("-" * 40)
        # Combine info about nulls and data types for a clean overview
        info_df = pd.DataFrame({
            'Data Type': self.df.dtypes,
            'Missing Values': self.df.isnull().sum(),
            '% Missing': (self.df.isnull().sum() / len(self.df) * 100).round(2)
        })
        print(info_df)
        print("\n")

        print("-" * 40)
        print("2. CARDINALITY (Unique values per categorical column)")
        print("-" * 40)
        # Cardinality helps us decide between One-Hot Encoding vs Label Encoding
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            print(f"{col}: {unique_count} unique values")
            
            # If cardinality is low, let's see the actual values
            if unique_count <= 10:
                print(f"   Values: {self.df[col].unique()}")

if __name__ == "__main__":
    # Ensure this runs relative to the project root
    RAW_DATA_PATH = os.path.join("data", "raw", "merged_jee_cutoff_2018_2025.csv")
    
    loader = DataLoader(RAW_DATA_PATH)
    try:
        df = loader.load_data()
        loader.inspect_data()
    except Exception as e:
        print(f"Error: {e}")
