import os
# pyrefly: ignore [missing-import]
import joblib
import pickle
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np

# Setup Global Cache to keep the servers lightning fast
_ARTIFACTS_CACHE = None                                # Globaly declared variable to store the loaded models and encoders in memory => This makes the app faster

# Function to load the trained models and encoders
def load_artifacts():
    """Loads all models and encoders into a global in-memory cache."""
    global _ARTIFACTS_CACHE
    if _ARTIFACTS_CACHE is not None:
        return _ARTIFACTS_CACHE
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, '..', 'models')
    
    artifacts = {}
    
    try:
        # Load IIT Artifacts
        artifacts['iit_model'] = joblib.load(os.path.join(models_dir, 'iit_model.pkl'))
        with open(os.path.join(models_dir, 'iit_encoders.pkl'), 'rb') as f:
            artifacts['iit_encoders'] = pickle.load(f)
            
        # Load NIT Artifacts
        artifacts['nit_model'] = joblib.load(os.path.join(models_dir, 'nit_model.pkl'))
        with open(os.path.join(models_dir, 'nit_encoders.pkl'), 'rb') as f:
            artifacts['nit_encoders'] = pickle.load(f)
            
        _ARTIFACTS_CACHE = artifacts
        return _ARTIFACTS_CACHE
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Models not found. Please run src/train.py first. Details: {e}")

def get_recommendations(user_rank: int, category: str, gender: str, exam_type: str, historical_df: pd.DataFrame, quota: str = 'OS'):
    """
    Candidate Generation + Batch ML Prediction System.
    Analyzes your rank, generates valid college branches, runs batch ML inference, and classifies safety tags.
    """
    # 1. Load Artifacts
    artifacts = load_artifacts()
    
    # Dynamic domain configuration
    if exam_type == 'Advanced':
        model = artifacts['iit_model']
        encoders = artifacts['iit_encoders']
        filter_quota = 'AI' # IITs use All India Quota
        domain_name = "IIT"
        # IIT mask
        domain_mask = historical_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False)
    else:
        model = artifacts['nit_model']
        encoders = artifacts['nit_encoders']
        filter_quota = quota # NITs use user provided quota (HS/OS)
        domain_name = "NIT/IIIT/GFTI"
        domain_mask = ~historical_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False)

    # 2. Candidate Generation / Filtering Phase
    # Search for valid seat configurations that matched the user's profile historically
    print(f"\n--- Running Recommendation Engine ({domain_name} Scope) ---")
    
    mask = (
        domain_mask &
        (historical_df['Seat Type'] == category) &
        (historical_df['Gender'] == gender) &
        (historical_df['Quota'] == filter_quota) &
        (historical_df['Closing Rank'] <= user_rank + 5000) # Buffer filter
    )
    
    candidates = historical_df[mask].copy()
    
    if candidates.empty:
        print("Warning: No candidates found within filtering parameters.")
        return []

    # Drop historical duplicates to keep only unique current branch configurations
    candidates = candidates.drop_duplicates(subset=['Institute', 'Academic Program Name'])
    
    print(f"Found {len(candidates)} unique branch candidates for evaluation...")

    # 3. Batch Data Preparation Phase
    # Force properties to 2026 simulation settings
    inference_df = pd.DataFrame({
        'Institute': candidates['Institute'],
        'Academic Program Name': candidates['Academic Program Name'],
        'Quota': filter_quota,
        'Seat Type': category,
        'Gender': gender,
        'Round': 6, # Predicting for final round
        'Year': 2026 # Simulating next year's cutoff
    })
    
    # Save raw records so we can build response dict with strings
    raw_meta = inference_df.copy()
    print("Raw metadata shape",raw_meta.shape)
    # Perform Batch Label Encoding
    for col, encoder in encoders.items():
        # Filter out items not present in the encoder vocab to avoid downstream crashes
        inference_df = inference_df[inference_df[col].isin(encoder.classes_)]
        
        # Encode the column in bulk
        inference_df[col] = encoder.transform(inference_df[col])
    print("Shape after encoding",inference_df.shape)
    # Synchronize metadata indices in case anything was purged in encoding filter
    raw_meta = raw_meta.loc[inference_df.index]
    print("Shape after synchronizing metadata indices",raw_meta.shape)
    if inference_df.empty:
        print("Warning: All candidates were filtered out by LabelEncoder vocabulary constraints.")
        return []

    # The Random Forest expects strict column ordering matching the original training setup
    # print("Inference DataFrame: \n",inference_df)
    expected_columns = ['Institute', 'Academic Program Name', 'Quota', 'Seat Type', 'Gender', 'Round', 'Year']
    inference_matrix = inference_df[expected_columns]
    # print("\n\nInference Matrix( Which is accutally using for prediction in the model)\n",inference_matrix)

    # 4. Batch Inference Phase (Ultra Efficient)
    print("Executing Batch Machine Learning Inference...")
    predicted_cutoffs = model.predict(inference_matrix)
    # print("\n\nPredicted cutoffs (Model's best guess)",predicted_cutoffs)
    print("Shape of predicted cutoffs",predicted_cutoffs.shape)
    print("Cutoffs",predicted_cutoffs[:5])  
    # 5. Bucket & Serialization Phase
    recommendations = []
    
    # Pre-compute predictions zip for linear construction
    for idx, pred_cutoff in zip(raw_meta.index, predicted_cutoffs):
        meta_row = raw_meta.loc[idx]
        pred_val = int(round(pred_cutoff))
        margin = pred_val - user_rank
        
        # Tagging logic
        if margin > 1500:
            tag = "Safe"
            sort_priority = 1
        elif margin >= -500:
            tag = "Target"
            sort_priority = 2
        else:
            tag = "Reach"
            sort_priority = 3
            
        recommendations.append({
            'institute': meta_row['Institute'],
            'program': meta_row['Academic Program Name'],
            'predicted_cutoff': pred_val,
            'margin': margin,
            'tag': tag,
            'sort_priority': sort_priority
        })

    # 6. Sort Phase (Safest first, then by margin descending)
    recommendations.sort(key=lambda x: (x['sort_priority'], -x['margin']))
    
    # Scrub sort helpers before returning
    for r in recommendations:
        r.pop('sort_priority')
        
    return recommendations

if __name__ == "__main__":
    from data_loader import DataLoader
    
    # 1. Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, '..', 'data', 'raw', 'merged_jee_cutoff_2018_2025.csv')
    
    try:
        # Load lookup DF
        loader = DataLoader(raw_path)
        df = loader.load_data()
        df = loader.basic_clean()
        
        # Simulated student profile
        RANK = 6000
        CAT = "OPEN"
        GEND = "Gender-Neutral"
        
        print(f"\n========== LOCAL ENGINE TEST ==========")
        print(f"Profile: Rank {RANK} | Cat: {CAT} | {GEND}")
        
        # Test IIT Engine
        iit_recs = get_recommendations(
            user_rank=RANK,
            category=CAT,
            gender=GEND,
            exam_type='Advanced',
            historical_df=df
        )
        
        print(f"\nTop 5 IIT recommendations for Rank {RANK}:")
        for rec in iit_recs[:5]:
            print(f"[{rec['tag']}] {rec['institute']} - {rec['program']}")
            print(f"       Predicted Cutoff: {rec['predicted_cutoff']} (Margin: {rec['margin']})")
            
        # Test NIT Engine
        nit_recs = get_recommendations(
            user_rank=RANK,
            category=CAT,
            gender=GEND,
            exam_type='Mains',
            historical_df=df,
            quota='OS'
        )
        
        print(f"\nTop 5 NIT recommendations for Rank {RANK}:")
        for rec in nit_recs[:5]:
            print(f"[{rec['tag']}] {rec['institute']} - {rec['program']}")
            print(f"       Predicted Cutoff: {rec['predicted_cutoff']} (Margin: {rec['margin']})")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test failed with error: {e}")
