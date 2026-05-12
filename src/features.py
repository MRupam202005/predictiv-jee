import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def preprocess_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies Label Encoding to categorical columns suitable for tree-based models
    and saves the fitted encoders to disk for inference.
    """
    print("-" * 40)
    print("FEATURE PREPROCESSING: LABEL ENCODING")
    print("-" * 40)
    
    # Work on a copy to avoid SettingWithCopyWarning
    df_encoded = df.copy()
    
    # Columns requested by the user
    categorical_cols = ['Institute', 'Academic Program Name', 'Type', 'Quota', 'Seat Type', 'Gender']
    
    # Filter only columns that actually exist in the dataframe
    cols_to_encode = [col for col in categorical_cols if col in df_encoded.columns]
    
    encoders = {}
    
    for col in cols_to_encode:
        print(f"  -> Encoding: {col}")
        le = LabelEncoder()
        
        # Convert to string to ensure LabelEncoder doesn't crash on hidden mixed types
        df_encoded[col] = df_encoded[col].astype(str)
        
        # Fit and transform
        df_encoded[col] = le.fit_transform(df_encoded[col])
        
        # Save the fitted encoder instance to our dictionary
        encoders[col] = le
        
    # Determine the path to the models/ directory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, '..', 'models')
    
    # Ensure the models directory exists (it should, due to our scaffolding)
    os.makedirs(models_dir, exist_ok=True)
    
    # Save the dictionary of encoders
    encoders_path = os.path.join(models_dir, 'label_encoders.pkl')
    with open(encoders_path, 'wb') as f:
        pickle.dump(encoders, f)
        
    print(f"\n[SUCCESS] Saved fitted Label Encoders to: {encoders_path}")
    print(f"[SUCCESS] Feature engineering complete. New Shape: {df_encoded.shape}\n")
    
    return df_encoded

def get_train_test_split(df: pd.DataFrame):
    """
    Separates the features (X) from the target (y) and splits them into
    training (80%) and testing (20%) sets.
    """
    print("-" * 40)
    print("TRAIN-TEST SPLIT")
    print("-" * 40)
    
    # Target variable is Closing Rank
    target = 'Closing Rank'
    
    # We must explicitly separate X and y
    y = df[target]
    
    # X contains everything except the target
    # Crucially, 'Opening Rank' is left inside X as it's our strongest predictor
    X = df.drop(columns=[target])
    
    print(f"Features (X) columns: {list(X.columns)}")
    print(f"Target (y) column: {target}")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape:  {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape:  {y_test.shape}\n")
    
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # A quick standalone test block
    from data_loader import DataLoader
    
    # Path relative to the script execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, '..', 'data', 'raw', 'merged_jee_cutoff_2018_2025.csv')
    
    try:
        loader = DataLoader(raw_path)
        df_raw = loader.load_data()
        
        # Basic cleaning (dropping null ranks as decided earlier)
        df_clean = df_raw.dropna(subset=['Opening Rank', 'Closing Rank']).copy()
        
        # Standardize gender before encoding
        if 'Gender' in df_clean.columns:
            df_clean['Gender'] = df_clean['Gender'].replace('F', 'Female-only (including Supernumerary)')
            
        # Apply our new feature preprocessing
        df_encoded = preprocess_features(df_clean)
        
        # Test the train-test split
        X_train, X_test, y_train, y_test = get_train_test_split(df_encoded)
        
        # Display a sample of the transformed data
        print("Sample of encoded features (X_train):")
        print(X_train.head())
        
    except Exception as e:
        print(f"Error during execution: {e}")
