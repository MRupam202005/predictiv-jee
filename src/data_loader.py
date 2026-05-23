import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
import os

class DataLoader:
    """
    1. Class to handle the loading and initial inspection of the raw JoSAA dataset.
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
        print(f"Data successfully loaded. Shape: (Rows, Columns) {self.df.shape}\n")
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
        print(info_df.head(10))
        print("\n")

        print("-" * 40)
        print("2. CARDINALITY")
        print("-" * 40)
        # Cardinality helps us decide between One-Hot Encoding vs Label Encoding
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            print(f"{col}: {unique_count} unique values")
            
            # If cardinality is low, let's see the actual values
            if unique_count <= 10:
                print(f"   Values: {self.df[col].unique()}")

    def basic_clean(self) -> pd.DataFrame:
        """
        Drops rows with missing Open/Close ranks and standardizes Gender strings.
        This provides a clean dataset ready for Label Encoding.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        print("Performing basic cleaning...")
        initial_len = len(self.df)
        self.df = self.df.dropna(subset=['Opening Rank', 'Closing Rank'])
        print(f"  -> Dropped {initial_len - len(self.df)} rows due to missing Ranks.")

        if 'Gender' in self.df.columns:
            self.df['Gender'] = self.df['Gender'].replace(
                'F', 'Female-only (including Supernumerary)'
            )
            print("  -> Standardized 'Gender' column values.")
            
        return self.df

    def clean_and_encode(self) -> pd.DataFrame:
        """
        Cleans the data and applies encoding:
        1. Drops rows with missing Open/Close ranks.
        2. Standardizes Gender strings.
        3. Applies One-Hot Encoding to low-cardinality categoricals.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("-" * 40)
        print("3. CLEANING & ENCODING")
        print("-" * 40)
        
        # 1. Drop Missing Values
        initial_len = len(self.df)
        self.df = self.df.dropna(subset=['Opening Rank', 'Closing Rank'])
        print(f"Dropped {initial_len - len(self.df)} rows due to missing Ranks.")

        # 2. Standardize Dirty Data (Gender)
        if 'Gender' in self.df.columns:
            self.df['Gender'] = self.df['Gender'].replace(
                'F', 'Female-only (including Supernumerary)'
            )
            print("Standardized 'Gender' column values.")

        # 3. One-Hot Encoding (OHE)
        cols_to_encode = ['Gender', 'Seat Type', 'Quota']
        cols_to_encode = [c for c in cols_to_encode if c in self.df.columns]
        
        print(f"Applying One-Hot Encoding to: {cols_to_encode}") 
        # pd.get_dummies converts categorical variables into dummy/indicator variables
        self.df = pd.get_dummies(self.df, columns=cols_to_encode, dummy_na=False, dtype=int)
        
        print(f"New Data Shape: (Rows, Columns) {self.df.shape}")
        return self.df

if __name__ == "__main__":   # Test the loader independently
    # Ensure this runs relative to the project root
    RAW_DATA_PATH = os.path.join("data", "raw", "merged_jee_cutoff_2018_2025.csv")
    loader = DataLoader(RAW_DATA_PATH)
    try:
        df = loader.load_data()
        loader.inspect_data()
        clean_df = loader.clean_and_encode()
    except Exception as e:
        print(f"Error: {e}")

