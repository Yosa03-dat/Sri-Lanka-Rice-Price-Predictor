import sys
from pathlib import Path

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from Data_Preprocessing.paths import PREPROCESSED_PATHS


_INGESTION_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PREPROCESSED_PATHS["processed_full_features"]
FEATURE_COLS_PATH = str(_INGESTION_PROJECT_ROOT / "feature_columns.json")

def get_latest_date():
    """Reads the last recorded timestamp from the master dataset."""
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Master dataset '{DATASET_PATH}' not found.")
    
    df = pd.read_csv(DATASET_PATH, index_col=0, parse_dates=True)
    latest_date = df.index.max()
    return latest_date, df

def scrape_cbsl_exchange_rate(target_date: datetime) -> float:
    """
    Scrapes or fetches the USD/LKR exchange rate.
    Falls back to public financial API or forward-filling if unavailable.
    """
    try:
        # Example API/Scraper hook (replace with direct portal endpoint)
        url = f"https://api.exchangerate.host/{target_date.strftime('%Y-%m-%d')}?base=USD&symbols=LKR"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'LKR' in data['rates']:
                return float(data['rates']['LKR'])
    except Exception as e:
        print(f"[Warning] Live exchange rate scraping failed: {e}")
    
    return None

def determine_sri_lanka_season(date: datetime) -> str:
    """Identifies the agricultural cultivation season (Maha or Yala)."""
    month = date.month
    year = date.year
    # Maha season: September to March
    if month >= 9:
        return f"season_{year}-{year+1}Maha"
    elif month <= 3:
        return f"season_{year-1}-{year}Maha"
    # Yala season: April to August
    else:
        return f"season_{year}Yala"

def ingest_next_week_data(manual_inputs: dict = None):
    """
    Steps +7 days from last date, builds the delta record,
    runs preprocessing, and appends to the master dataset.
    """
    latest_date, df = get_latest_date()
    next_date = latest_date + timedelta(days=7)
    date_str = next_date.strftime('%Y-%m-%d')
    print(f"Targeting new weekly row for date: {date_str}")

    # 1. Fetch live metrics
    scraped_fx = scrape_cbsl_exchange_rate(next_date)
    
    # 2. Extract or prompt for values
    new_row = {}
    
    # Fallback to last known value or manual input if scraping missed
    if manual_inputs and 'Exchange_Rate' in manual_inputs:
        fx_val = float(manual_inputs['Exchange_Rate'])
    elif scraped_fx is not None:
        fx_val = scraped_fx
    else:
        # Forward fill from previous record if unavailable
        fx_val = df['Exchange_Rate'].iloc[-1] if 'Exchange_Rate' in df.columns else 300.0
        print(f"[Notice] Forward-filling Exchange_Rate with: {fx_val}")

    new_row['Exchange_Rate'] = fx_val

    # 3. Delta Feature Engineering
    # 30-day (4-week) rolling percentage change
    if 'Exchange_Rate' in df.columns and len(df) >= 4:
        past_fx = df['Exchange_Rate'].iloc[-4]
        new_row['Exchange_Rate_30d_PctChange'] = ((fx_val - past_fx) / past_fx) * 100.0
    else:
        new_row['Exchange_Rate_30d_PctChange'] = 0.0

    # Add seasonal indicators
    season_col = determine_sri_lanka_season(next_date)
    for col in df.columns:
        if col.startswith('season_'):
            new_row[col] = 1.0 if col == season_col else 0.0

    # Fill remaining macro features from manual inputs or forward-fill
    for col in df.columns:
        if col not in new_row and col not in ['log_price', 'real_price_lkr', 'target_volatility', 'log_return']:
            if manual_inputs and col in manual_inputs:
                new_row[col] = float(manual_inputs[col])
            else:
                # Forward-fill stable macro metrics (e.g., CBSL wages, production statistics)
                new_row[col] = df[col].iloc[-1]

    # Target price assignment if actual price is known (for training history)
    if manual_inputs and 'real_price_lkr' in manual_inputs:
        actual_price = float(manual_inputs['real_price_lkr'])
        new_row['real_price_lkr'] = actual_price
        new_row['log_price'] = np.log(actual_price)
    else:
        new_row['real_price_lkr'] = np.nan
        new_row['log_price'] = np.nan

    # 4. Append to DataFrame and Save
    new_df_row = pd.DataFrame([new_row], index=[pd.to_datetime(date_str)])
    new_df_row.index.name = df.index.name if df.index.name else 'Report_Date'
    
    updated_df = pd.concat([df, new_df_row])
    updated_df = updated_df[~updated_df.index.duplicated(keep='last')]
    updated_df.to_csv(DATASET_PATH)

    return {
        "status": "success",
        "added_date": date_str,
        "features_populated": len(new_row)
    }