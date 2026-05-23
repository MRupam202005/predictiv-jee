import os
# pyrefly: ignore [missing-import]
import joblib
# pyrefly: ignore [missing-import]
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Import our custom modules
from data_loader import DataLoader
from features import split_and_preprocess

def train_and_evaluate_model(X_train, X_test, y_train, y_test, name):
    """Initializes, trains, and evaluates the Random Forest model."""
    print(f"\nInitializing Random Forest Regressor for {name} (100 trees)...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    print(f"Starting {name} training on {len(X_train)} rows. This may take a minute...")
    start_time = time.time()
    rf_model.fit(X_train, y_train)
    end_time = time.time()
    
    print(f"[SUCCESS] {name} Training Complete! It took {(end_time - start_time):.2f} seconds.")
    
    print(f"Evaluating {name} Model on Test Set...")
    y_pred = rf_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("-" * 40)
    print(f"{name} MODEL METRICS")
    print("-" * 40)
    print(f"Mean Absolute Error (MAE): {mae:.2f} ranks")
    print(f"R-squared (R²): {r2:.4f}")
    
    return rf_model

def save_model(model, filename):
    """
    Saves the trained model to the models/ directory using joblib.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    file_path = os.path.join(models_dir, filename)
    print(f"\nSaving model to {file_path}...")
    joblib.dump(model, file_path)
    print(f"[SUCCESS] Model saved successfully to {filename}!")

if __name__ == "__main__":
    print("=== STARTING DUAL-MODEL TRAINING PIPELINE ===\n")
    
    # 1. Load Data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, '..', 'data', 'raw', 'merged_jee_cutoff_2018_2025.csv')
    loader = DataLoader(raw_path)
    raw_df = loader.load_data()
    
    # 2. Basic Clean
    clean_df = loader.basic_clean()
    
    # 3. Split & Encode Features
    print("\nExtracting and splitting datasets...")
    (X_train_iit, X_test_iit, y_train_iit, y_test_iit, 
     X_train_nit, X_test_nit, y_train_nit, y_test_nit) = split_and_preprocess(clean_df)
    
    # 4. Train and Evaluate Models
    print("\n--- TRAINING & EVALUATION Phase ---")
    model_iit = train_and_evaluate_model(X_train_iit, X_test_iit, y_train_iit, y_test_iit, "IIT")
    model_nit = train_and_evaluate_model(X_train_nit, X_test_nit, y_train_nit, y_test_nit, "NIT/IIIT/GFTI")
    
    # 5. Save Models
    print("\n--- SAVING Phase ---")
    save_model(model_iit, "iit_model.pkl")
    save_model(model_nit, "nit_model.pkl")
    
    print("\n=== DUAL PIPELINE COMPLETE ===")
