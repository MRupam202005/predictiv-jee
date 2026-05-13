import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def split_and_preprocess(df: pd.DataFrame):
    """
    1. Splits data into IITs vs NIT/IIIT/GFTIs.
    2. Drops 'Opening Rank' to prevent data leakage.
    3. Label Encodes both datasets independently.
    4. Saves encoders to disk.
    5. Returns train/test splits for both datasets.
    """
    print("-" * 40)
    print("FEATURE PREPROCESSING & DATA SPLIT")
    print("-" * 40)
    
    # Drop Opening Rank globally
    if 'Opening Rank' in df.columns:
        df = df.drop(columns=['Opening Rank'])
        print("Dropped 'Opening Rank' to prevent data leakage.")
        
    # Split into IITs and non-IITs
    # "Indian Institute of Technology" captures IITs (e.g. "Indian Institute of Technology Bombay")
    # NITs, IIITs, and GFTIs will not match this string.
    iit_mask = df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False)
    
    df_iit = df[iit_mask].copy()
    df_nit = df[~iit_mask].copy()
    
    print(f"Data split complete:")
    print(f"  -> IIT Dataset shape: {df_iit.shape}")
    print(f"  -> NIT+ Dataset shape: {df_nit.shape}")
    
    categorical_cols = ['Institute', 'Academic Program Name', 'Quota', 'Seat Type', 'Gender']
    
    # Helper function to encode and save
    def encode_and_save(domain_df, prefix):
        encoders = {}
        cols_to_encode = [col for col in categorical_cols if col in domain_df.columns]
        
        for col in cols_to_encode:
            le = LabelEncoder()
            domain_df[col] = domain_df[col].astype(str)
            domain_df[col] = le.fit_transform(domain_df[col])
            encoders[col] = le
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, '..', 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        encoders_path = os.path.join(models_dir, f'{prefix}_encoders.pkl')
        with open(encoders_path, 'wb') as f:
            pickle.dump(encoders, f)
            
        print(f"Saved {prefix.upper()} Label Encoders to: {encoders_path}")
        return domain_df

    print("\nEncoding IIT Dataset...")
    df_iit_encoded = encode_and_save(df_iit, 'iit')
    
    print("\nEncoding NIT/IIIT/GFTI Dataset...")
    df_nit_encoded = encode_and_save(df_nit, 'nit')
    
    # Helper function to split
    def perform_split(encoded_df, name):
        target = 'Closing Rank'
        y = encoded_df[target]
        X = encoded_df.drop(columns=[target])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )
        print(f"{name} Train shape: {X_train.shape}, Test shape: {X_test.shape}")
        return X_train, X_test, y_train, y_test
        
    print("\nPerforming Train-Test Splits...")
    X_train_iit, X_test_iit, y_train_iit, y_test_iit = perform_split(df_iit_encoded, "IIT")
    X_train_nit, X_test_nit, y_train_nit, y_test_nit = perform_split(df_nit_encoded, "NIT")
    
    return (X_train_iit, X_test_iit, y_train_iit, y_test_iit, 
            X_train_nit, X_test_nit, y_train_nit, y_test_nit)

if __name__ == "__main__":
    from data_loader import DataLoader
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, '..', 'data', 'raw', 'merged_jee_cutoff_2018_2025.csv')
    
    try:
        loader = DataLoader(raw_path)
        df_raw = loader.load_data()
        df_clean = loader.basic_clean()
        
        outputs = split_and_preprocess(df_clean)
        print("\nSuccessfully returned 8 output variables from split_and_preprocess!")
        
    except Exception as e:
        print(f"Error during execution: {e}")
