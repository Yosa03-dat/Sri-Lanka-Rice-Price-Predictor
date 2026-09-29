from __future__ import annotations

import pandas as pd

from paths import PREPROCESSED_PATHS, save_dataset


def _load_indexed(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Report_Date"] = pd.to_datetime(df["Report_Date"])
    return df.set_index("Report_Date").sort_index()


def _load_annual(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Report_Date" in df.columns:
        df = df.rename(columns={"Report_Date": "Year"})
    return df


def expand_annual_to_daily(annual_df: pd.DataFrame, daily_index: pd.DatetimeIndex) -> pd.DataFrame:
    annual = annual_df.copy()
    if annual.index.name != "Year" and "Year" in annual.columns:
        annual = annual.set_index("Year")
    annual.index = annual.index.astype(int)

    daily = pd.DataFrame(index=daily_index)
    daily["Year"] = daily.index.year
    merged = daily.join(annual, on="Year").drop(columns=["Year"])
    return merged.ffill().bfill()


def build_final_dataset(save: bool = True) -> pd.DataFrame:
    pettah = _load_indexed(PREPROCESSED_PATHS["harti_pettah"])
    dcs = _load_indexed(PREPROCESSED_PATHS["dcs_daily"])
    exchange = _load_indexed(PREPROCESSED_PATHS["exchange_daily"])
    weather = _load_indexed(PREPROCESSED_PATHS["weather_daily"])
    wfp = _load_indexed(PREPROCESSED_PATHS["wfp_daily"])
    faostat = _load_annual(PREPROCESSED_PATHS["faostat_annual"])
    cbsl = (
        _load_annual(PREPROCESSED_PATHS["cbsl_annual"])
        if PREPROCESSED_PATHS["cbsl_annual"].exists()
        else None
    )

    core = pettah.join(dcs, how="left").dropna(subset=["Total_Production_MT"])
    core = core.join(exchange[["Exchange_Rate"]], how="left")
    core["Exchange_Rate"] = core["Exchange_Rate"].ffill()
    core["Exchange_Rate_30d_PctChange"] = core["Exchange_Rate"].pct_change(periods=30) * 100
    core = core.join(weather, how="left")

    required_cols = [
        "Exchange_Rate",
        "Exchange_Rate_30d_PctChange",
        "Rainfall_mm",
        "Temp_Max_C",
        "Temp_Min_C",
    ]
    core = core.dropna(subset=[col for col in required_cols if col in core.columns])

    final = core.join(wfp, how="left")
    final = final.join(expand_annual_to_daily(faostat, final.index), how="left")

    if PREPROCESSED_PATHS["cbsl_annual"].exists():
        final = final.join(expand_annual_to_daily(cbsl, final.index), how="left")

    if save:
        save_dataset(final, PREPROCESSED_PATHS["final_integrated"])

    return final


if __name__ == "__main__":
    result = build_final_dataset()
    print(f"Saved: {PREPROCESSED_PATHS['final_integrated']}")
    print(f"Shape: {result.shape}")
    print(f"Date range: {result.index.min().date()} to {result.index.max().date()}")
