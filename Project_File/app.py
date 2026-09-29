import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from xgboost import XGBRegressor

from ingestion import (
    get_latest_date, 
    ingest_next_week_data, 
    DATASET_PATH, 
    FEATURE_COLS_PATH
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = str(_PROJECT_ROOT / "xgb_real_price.json")

xgb_model = None

def load_trained_model():
    global xgb_model
    if os.path.exists(MODEL_PATH):
        xgb_model = XGBRegressor()
        xgb_model.load_model(MODEL_PATH)
        print("[Engine] XGBoost model loaded successfully.")
    else:
        print("[Warning] No saved model found. Please trigger /retrain.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_trained_model()
    yield

app = FastAPI(
    title="Sri Lankan Rice Price Forecasting Engine",
    description="Automated ingestion, retraining, and inference API for agricultural commodity forecasting.",
    version="1.0.0",
    lifespan=lifespan
)

# Pydantic Schemas
class SyncDataRequest(BaseModel):
    manual_inputs: Optional[Dict[str, float]] = None

class PredictRequest(BaseModel):
    features: Optional[Dict[str, float]] = None

# API Endpoints
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Sri Lankan Rice Price Forecasting API is active. Visit /docs for documentation."
    }

@app.get("/health")
def health_check():
    return {"status": "online", "model_loaded": xgb_model is not None}

@app.get("/latest-date")
def fetch_latest_date():
    try:
        latest_date, _ = get_latest_date()
        return {
            "latest_date": latest_date.strftime('%Y-%m-%d'),
            "next_target_date": (latest_date + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-weekly-data")
def sync_weekly_data(payload: SyncDataRequest):
    try:
        result = ingest_next_week_data(manual_inputs=payload.manual_inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data sync failed: {str(e)}")

def background_retrain_task():
    global xgb_model
    print("[Retrain] Loading full updated dataset...")
    df = pd.read_csv(DATASET_PATH, index_col=0, parse_dates=True)

    # Ensure real_price_lkr column exists and is populated
    if 'real_price_lkr' not in df.columns:
        df['real_price_lkr'] = np.exp(df['log_price']) if 'log_price' in df.columns else np.nan
    else:
        if 'log_price' in df.columns:
            df['real_price_lkr'] = df['real_price_lkr'].fillna(np.exp(df['log_price']))

    TARGET = 'real_price_lkr'
    
    cols_to_drop = [
        'target_volatility', 'log_return', 'log_price', 'volatility_4p',
        'volatility_8p', 'volatility_12p', 'log_return_lag1', 'log_return_lag2',
        'log_return_lag4', 'log_price_lag1', 'log_price_lag2', 'log_price_lag4',
        'Exchange_Rate', 'Exchange_Rate_lag1', 'Exchange_Rate_lag2', 'Exchange_Rate_lag4'
    ]
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]

    X = df.drop(columns=cols_to_drop + [TARGET])
    y = df[TARGET]

    # Clean missing values for valid historical training
    valid_target = ~y.isna()
    X_clean = X.loc[valid_target].select_dtypes(include=['number', 'bool'])
    y_clean = y.loc[valid_target]

    X_clean = X_clean.ffill().bfill().astype(float)
    valid_idx = X_clean.dropna().index.intersection(y_clean.dropna().index)
    
    X_train = X_clean.loc[valid_idx]
    y_train = y_clean.loc[valid_idx]

    feature_list = list(X_train.columns)
    # Save feature columns back to the project root
    feature_cols_save_path = str(_PROJECT_ROOT / "feature_columns.json")
    with open(feature_cols_save_path, "w") as f:
        json.dump(feature_list, f)

    print(f"[Retrain] Fitting model on {len(X_train)} historical records...")
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)

    model.save_model(MODEL_PATH)
    xgb_model = model
    print("[Retrain] Model updated and serialized successfully.")

@app.post("/retrain")
def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_retrain_task)
    return {"message": "Retraining started in the background. The model will update automatically upon completion."}

@app.post("/predict")
def predict_price(payload: PredictRequest):
    global xgb_model
    if xgb_model is None:
        load_trained_model()
        if xgb_model is None:
            raise HTTPException(status_code=400, detail="Model is not trained yet. Trigger /retrain first.")

    try:
        if not os.path.exists(FEATURE_COLS_PATH):
            raise HTTPException(status_code=500, detail="Feature schema file not found. Please retrain.")

        with open(FEATURE_COLS_PATH, "r") as f:
            expected_features = json.load(f)

        if payload.features:
            input_df = pd.DataFrame([payload.features])
            target_date = "Custom Input"
        else:
            df = pd.read_csv(DATASET_PATH, index_col=0, parse_dates=True)
            input_df = df.iloc[[-1]]
            # The prediction is for the NEXT week after the last data point
            last_date = input_df.index[0]
            if isinstance(last_date, (pd.Timestamp, datetime)):
                target_date = (last_date + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            else:
                target_date = str(last_date)

        for col in expected_features:
            if col not in input_df.columns:
                input_df[col] = 0.0

        aligned_X = input_df[expected_features].astype(float)
        prediction = float(xgb_model.predict(aligned_X)[0])

        return {
            "predicted_price_lkr": round(prediction, 2),
            "target_date": target_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Date Status — tells frontend if sync is allowed
@app.get("/date-status")
def get_date_status():
    try:
        latest_date, _ = get_latest_date()
        today = datetime.now().date()
        next_prediction = latest_date.date() + pd.Timedelta(days=7)
        max_allowed    = today + pd.Timedelta(days=7)
        sync_allowed   = next_prediction <= max_allowed

        return {
            "today":            today.strftime('%Y-%m-%d'),
            "latest_data_date": latest_date.strftime('%Y-%m-%d'),
            "next_prediction":  next_prediction.strftime('%Y-%m-%d'),
            "max_allowed":      max_allowed.strftime('%Y-%m-%d'),
            "sync_allowed":     sync_allowed,
            "days_ahead":       (next_prediction - today).days,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New: Historical price chart data
CHART_VARIETIES = ['Samba 1', 'Samba 2', 'Nadu 1', 'Nadu 2', 'Raw White', 'Raw red', 'Imported Rice']

@app.get("/history")
def get_price_history(days: int = 730):
    try:
        df = pd.read_csv(DATASET_PATH, index_col=0, parse_dates=True)

        if 'real_price_lkr' not in df.columns or df['real_price_lkr'].isna().all():
            df['real_price_lkr'] = np.exp(df['log_price'])

        cutoff = df.index.max() - pd.Timedelta(days=days)
        sub = df[df.index >= cutoff].copy()

        series = {}
        for col in CHART_VARIETIES:
            if col in sub.columns:
                vals = sub[col].ffill().tolist()
                series[col] = [round(v, 2) if pd.notna(v) else None for v in vals]

        composite = sub['real_price_lkr'].ffill().tolist()
        series['Composite'] = [round(v, 2) if pd.notna(v) else None for v in composite]

        labels = [d.strftime('%Y-%m-%d') for d in sub.index]

        return {
            "labels": labels,
            "series": series,
            "count": len(labels)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History fetch failed: {str(e)}")



# Price lookup by date

@app.get("/history/{query_date}")
def get_price_by_date(query_date: str):
    try:
        df = pd.read_csv(DATASET_PATH, index_col=0, parse_dates=True)

        if 'real_price_lkr' not in df.columns or df['real_price_lkr'].isna().all():
            df['real_price_lkr'] = np.exp(df['log_price'])

        try:
            target_dt = pd.to_datetime(query_date)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        if target_dt < df.index.min():
            raise HTTPException(status_code=400, detail=f"Date is before dataset start ({df.index.min().date()}).")
        if target_dt > df.index.max() + pd.Timedelta(days=6):
            raise HTTPException(status_code=400, detail=f"Date is beyond dataset end ({df.index.max().date()}).")

        diff = (df.index - target_dt).map(abs)
        nearest_idx = diff.argmin()
        row = df.iloc[nearest_idx]
        actual_date = df.index[nearest_idx]
        exact_match = actual_date == target_dt

        varieties = {}
        for col in CHART_VARIETIES:
            if col in df.columns and pd.notna(row[col]):
                varieties[col] = round(float(row[col]), 2)

        return {
            "queried_date":  query_date,
            "actual_date":   actual_date.strftime('%Y-%m-%d'),
            "exact_match":   exact_match,
            "composite_price_lkr": round(float(row['real_price_lkr']), 2) if pd.notna(row['real_price_lkr']) else None,
            "varieties":     varieties,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lookup failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)