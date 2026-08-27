from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "Raw_data"
PREPROCESSED_ROOT = PROJECT_ROOT / "Preprocessed_data"

RAW_PATHS = {
    "harti_rice": RAW_ROOT / "Harti_Data" / "FINAL_rice_data_2015_2026.csv",
    "dcs_paddy": RAW_ROOT
    / "Paddy_metric_data_satistics_page"
    / "dcs_paddy_metric_statistics_2015_2026.csv",
    "exchange_rates": RAW_ROOT / "Exchange_rates_Data" / "exchange_rates.csv",
    "weather": RAW_ROOT / "Weather_Data" / "weather_data_2015_2025.csv",
    "wfp_prices": RAW_ROOT / "WFP_Data" / "wfp_food_prices_lka.csv",
    "faostat_dir": RAW_ROOT / "FAOSTAT_Data",
    "cbsl_producer_prices": RAW_ROOT / "CBSL_Data" / "ess_2025_table3.7_e.xlsx",
    "cbsl_daily_wages": RAW_ROOT / "CBSL_Data" / "ess_2025_table3.11_e.xlsx",
    "cbsl_monthly_wages": RAW_ROOT / "CBSL_Data" / "ess_2025_table3.15_e.xlsx",
}

PREPROCESSED_PATHS = {
    "harti_pettah": PREPROCESSED_ROOT / "harti_pettah_rice_timeseries.csv",
    "harti_marandagahamula": PREPROCESSED_ROOT / "harti_marandagahamula_rice_timeseries.csv",
    "harti_pettah_long": PREPROCESSED_ROOT / "harti_pettah_rice_long.csv",
    "harti_marandagahamula_long": PREPROCESSED_ROOT / "harti_marandagahamula_rice_long.csv",
    "harti_unit_log": PREPROCESSED_ROOT / "harti_unit_conversion_log.csv",
    "dcs_daily": PREPROCESSED_ROOT / "dcs_daily_supply.csv",
    "exchange_daily": PREPROCESSED_ROOT / "exchange_rates_daily.csv",
    "weather_daily": PREPROCESSED_ROOT / "weather_daily.csv",
    "wfp_daily": PREPROCESSED_ROOT / "wfp_daily_2015_2026.csv",
    "faostat_annual": PREPROCESSED_ROOT / "faostat_annual_summary_2015_2026.csv",
    "cbsl_annual": PREPROCESSED_ROOT / "cbsl_annual_features.csv",
    "final_integrated": PREPROCESSED_ROOT / "final_integrated_data.csv",
    "processed_train": PREPROCESSED_ROOT / "processed_train.csv",
    "processed_test": PREPROCESSED_ROOT / "processed_test.csv",
    "processed_full_features": PREPROCESSED_ROOT / "processed_full_features.csv",
}

RICE_ITEMS = [
    "Samba 1",
    "Samba 2",
    "Keeri Samba",
    "Nadu 1",
    "Nadu 2",
    "Raw red",
    "Raw White",
    "Imported Rice",
    "Ponne Samba",
    "Nadu",
]

WFP_COMMODITIES = [
    "Rice (long grain)",
    "Rice (medium grain)",
    "Rice (red nadu)",
    "Rice (red)",
    "Rice (white)",
    "Fuel (diesel)",
    "Fuel (petrol-gasoline)",
]

PROJECT_START_DATE = "2015-01-01"
INTEGRATION_END_DATE = "2026-12-31"


def save_dataset(df, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out.index.name = "Report_Date"
    out.to_csv(path, index=True)
