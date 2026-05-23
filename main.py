# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
import sys
import os
import pandas as pd

# Add root to path so we can resolve local imports reliably
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.data_loader import DataLoader
from src.predict import get_recommendations, load_artifacts

# GLOBAL CACHE: Warm boot lookup stores
HISTORICAL_DF = None

print("\n--- INITIALIZING RECON ENGINE BOOT SEQUENCE ---")
try:
    # Pre-warm model weights so inference is instant
    print(" -> Warming Artifact memory...")
    load_artifacts()
    
    # Pre-warm candidates pool so candidate generation doesn't require disk read operations
    print(" -> Warming Candidate Generator database cache...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, 'data', 'raw', 'merged_jee_cutoff_2018_2025.parquet')
    loader = DataLoader(raw_path)
    raw_df = loader.load_data()
    HISTORICAL_DF = loader.basic_clean()
    print(f" -> Core Database Cached successfully ({len(HISTORICAL_DF)} rows ready).")
    print("--- ENGINE DEPLOYED SUCCESSFULLY ---\n")
    
except Exception as e:
    print(f"!!! BOOT WARNING: Engine caching failed. Errors: {e} !!!\n")

app = FastAPI(
    title="Predictiv-Jee API",
    description="High-Performance College Recommendation & Predictive ML Cutoffs engine."
)

# Allow ALL origins during local development.
# To lock down in production: replace "*" with your deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentRequest(BaseModel):
    """
    Enforces structure for user-centric prediction requests.
    We no longer need the user to input specific college names!
    """
    user_rank: int = Field(..., ge=1, description="Your JEE rank.")
    category: str = Field(..., description="Category pool (e.g. OPEN, OBC-NCL, SC, ST).")
    gender: str = Field(..., description="Gender Pool (Gender-Neutral or Female-only).")
    exam_type: str = Field(..., description="Either 'Advanced' (IIT) or 'Mains' (NIT/IIIT/GFTI).")
    # Quota is optional and only applies to Mains (NITs)
    quota: str = Field(default="OS", description="Applies to Mains only (OS for Other State, HS for Home State).")

class TrendRequest(BaseModel):
    """
    Enforces structure for historical trend requests for a specific branch.
    """
    institute: str
    program: str
    category: str
    gender: str
    quota: str

@app.get("/")
def health_check():
    return {"status": "Predictiv-Jee Recommendation Engine is active"}

@app.get("/api/options")
def get_options():
    """
    Returns the unique values for Category and Gender directly from the historical data.
    This guarantees the frontend dropdowns perfectly match what the ML model expects.
    """
    if HISTORICAL_DF is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Candidate caching initialization failed.")
        
    try:
        # Extract unique values from the dataframe
        categories = sorted(HISTORICAL_DF['Seat Type'].dropna().unique().tolist())
        genders = sorted(HISTORICAL_DF['Gender'].dropna().unique().tolist())
        
        return {
            "categories": categories,
            "genders": genders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch filter options: {str(e)}")

@app.post("/api/predict")
def predict_recommendations(payload: StudentRequest):
    """
    Dynamic Recommendation Endpoint:
    1. Ingests candidate user data.
    2. Extracts match candidates from cache.
    3. Predicts 2026 cutoffs using production Dual Random Forests.
    4. Classifies & ranks items by safety margins.
    """
    if HISTORICAL_DF is None:
        raise HTTPException(
            status_code=503, 
            detail="Service Unavailable: Candidate caching initialization failed."
        )
        
    try:
        # Call our batch processing backend routine
        results = get_recommendations(
            user_rank=payload.user_rank,
            category=payload.category,
            gender=payload.gender,
            exam_type=payload.exam_type,
            historical_df=HISTORICAL_DF,
            quota=payload.quota
        )
        
        return {
            "user_query": {
                "rank": payload.user_rank,
                "category": payload.category,
                "exam_type": payload.exam_type
            },
            "total_matches": len(results),
            "recommendations": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline failed: {str(e)}")

@app.post("/api/trends")
def get_historical_trends(payload: TrendRequest):
    """
    Returns historical closing ranks for a specific college branch
    over the available years (2018-2025).
    Takes the maximum round (Round 6) data for each year.
    """
    if HISTORICAL_DF is None:
        raise HTTPException(status_code=503, detail="Service Unavailable: Candidate caching initialization failed.")
        
    try:
        # Filter the historical dataframe
        mask = (
            (HISTORICAL_DF['Institute'] == payload.institute) &
            (HISTORICAL_DF['Academic Program Name'] == payload.program) &
            (HISTORICAL_DF['Seat Type'] == payload.category) &
            (HISTORICAL_DF['Gender'] == payload.gender) &
            (HISTORICAL_DF['Quota'] == payload.quota)
        )
        
        filtered = HISTORICAL_DF[mask].copy()
        
        if filtered.empty:
            return {"trends": []}
            
        # For each year, we want the final round's closing rank
        # Sort by year and round, then drop duplicates keeping the last round
        trends = filtered.sort_values(by=['Year', 'Round']).drop_duplicates(subset=['Year'], keep='last')
        
        # Format the output for the charting library
        trend_data = []
        for _, row in trends.iterrows():
            trend_data.append({
                "year": int(row['Year']),
                "closing_rank": int(row['Closing Rank'])
            })
            
        return {"trends": trend_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")
