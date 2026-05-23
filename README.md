# 🎓 Predictiv-JEE: ML-Powered College Recommendation Engine

![Tech Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20Scikit--Learn-blue)
![Machine Learning](https://img.shields.io/badge/Algorithm-Dual%20Random%20Forests-success)
![Data Optimization](https://img.shields.io/badge/Data-Apache%20Parquet-orange)

## 📌 Overview
Predictiv-JEE is a full-stack, data-driven web application designed to help engineering aspirants in India predict their college admission chances. By leveraging **8 years of historical JoSAA/CSAB cutoff data (430,000+ rows)**, the platform uses Machine Learning to accurately predict future cutoffs and categorize colleges into `Safe`, `Target`, and `Reach` buckets based on a student's unique rank and demographic profile.

## 🚀 Key Features & Technical Highlights

### 1. Dual Machine Learning Pipeline
- Implemented split **Random Forest Regressors** (one for IITs, one for NIT/IIIT/GFTIs) to handle the fundamentally different rank scales of the Advanced vs. Mains exams.
- Engineered rigorous data pre-processing: purged "Opening Rank" to prevent inference-time data leakage, handled NaN inconsistencies, and standardized demographic strings across 8 years of scattered institutional data.

### 2. Big Data Performance Optimization
- Refactored the core data-loading engine to use **Apache Parquet (PyArrow)** instead of CSVs. 
- This compressed the data size by ~90%, preserved strict column data types, and reduced the Pandas boot-up load time from seconds to milliseconds.

### 3. High-Performance API Backend
- Built a deeply optimized **FastAPI** server that pre-loads all serialized models (`.pkl`), encoders, and Parquet data into RAM globally on boot.
- When a user requests recommendations, the API dynamically filters the database, vectorizes the candidates, and performs batch ML predictions instantly.

### 4. Premium React Frontend & Visualization
- Built a modern, responsive UI using **React, Vite, and Tailwind CSS**.
- **Dynamic Probability Engine:** Developed a custom mathematical algorithm that translates ML cutoff margins into visual admission percentages (0-99%), rendered via interactive SVG progress rings.
- **Historical Trend Charts:** Integrated **Recharts** to plot 8-year historical closing rank trends per branch, beautifully overlaying the ML's future prediction.

## 🛠️ Technology Stack
- **Frontend:** React.js, Vite, Tailwind CSS (v4), Recharts
- **Backend API:** Python, FastAPI, Uvicorn, Pydantic
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Data Engineering:** Apache Parquet
- **Deployment:** Dockerized architecture ready for PaaS/Cloud integration.

## 💻 Local Development Setup

### 1. Start the FastAPI Backend
```bash
# Clone the repository
git clone https://github.com/MRupam202005/predictiv-jee.git
cd predictiv-jee

# Create and activate a virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Boot the API server
uvicorn main:app --reload
```
*The API is now running at `http://127.0.0.1:8000`*

### 2. Start the React Frontend
```bash
# Open a new terminal instance
cd predictiv-jee/frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```
*The Application is now live at `http://localhost:5173`*
