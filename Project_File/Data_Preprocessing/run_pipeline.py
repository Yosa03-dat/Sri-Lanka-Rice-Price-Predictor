from __future__ import annotations

import re
import sys

import numpy as np
import pandas as pd

from harti_price_utils import coalesce_price_columns, preprocess_harti_prices
from integrate import build_final_dataset
from run_volatility_preprocessing import run_volatility_preprocessing
from paths import (
    INTEGRATION_END_DATE,
    PREPROCESSED_PATHS,
    PROJECT_START_DATE,
    RAW_PATHS,
    RICE_ITEMS,
    WFP_COMMODITIES,
    save_dataset,
)


def run_harti() -> None:
    print("1/7 Harti rice prices")
    df = pd.read_csv(RAW_PATHS["harti_rice"])
    df = df.dropna(subset=["Item"])
    df["Item"] = df["Item"].astype(str).str.strip()
    df = df[(df["Item"] != "") & df["Item"].isin(RICE_ITEMS)].copy()
    df["Report_Date"] = pd.to_datetime(df["Report_Date"])
    df = coalesce_price_columns(df, "Pettah_Average_Current", "Pettah_Average_Previous", "Pettah_Price")
    df = coalesce_price_columns(
        df,
        "Marandagahamula_Average_Current",
        "Marandagahamula_Average_Previous",
        "Marandagahamula_Price",
    )

    pettah, pettah_long, pettah_log = preprocess_harti_prices(df, "Pettah_Price", "Pettah")
    maranda, maranda_long, maranda_log = preprocess_harti_prices(df, "Marandagahamula_Price", "Marandagahamula")
    save_dataset(pettah, PREPROCESSED_PATHS["harti_pettah"])
    save_dataset(maranda, PREPROCESSED_PATHS["harti_marandagahamula"])
    pettah_long.to_csv(PREPROCESSED_PATHS["harti_pettah_long"], index=False)
    maranda_long.to_csv(PREPROCESSED_PATHS["harti_marandagahamula_long"], index=False)
    pd.concat([pettah_log, maranda_log], ignore_index=True).to_csv(
        PREPROCESSED_PATHS["harti_unit_log"], index=False
    )
    print(f"  Pettah wide: {pettah.shape}, non-null cells: {int(pettah.notna().sum().sum())}, long rows: {len(pettah_long)}")
    print(f"  Marandagahamula long rows: {len(maranda_long)}")


def run_dcs() -> None:
    print("2/7 DCS paddy supply")

    def assign_market_date(season_str: str) -> pd.Timestamp:
        if "Yala" in season_str:
            match = re.search(r"(\d{4})Yala", season_str, re.IGNORECASE)
            if match:
                return pd.to_datetime(f"{match.group(1)}-09-01")
        elif "Maha" in season_str:
            match = re.search(r"(\d{4})Maha", season_str, re.IGNORECASE)
            if match:
                return pd.to_datetime(f"{match.group(1)}-03-01")
        return pd.NaT

    df_dcs = pd.read_csv(RAW_PATHS["dcs_paddy"])
    df_national = (
        df_dcs.groupby("Season")
        .agg(
            Total_Production_MT=("Total_Production_MT", "sum"),
            Gross_Harvested_Total=("Gross_Harvested_Total", "sum"),
        )
        .reset_index()
    )
    df_national["National_Yield_Efficiency"] = (
        df_national["Total_Production_MT"] / df_national["Gross_Harvested_Total"]
    )
    df_national["Market_Date"] = df_national["Season"].apply(assign_market_date)
    df_national = df_national.dropna(subset=["Market_Date"]).sort_values("Market_Date").set_index("Market_Date")

    daily_idx = pd.date_range(start=df_national.index.min(), end=pd.to_datetime(INTEGRATION_END_DATE), freq="D")
    df_daily = pd.DataFrame(index=daily_idx)
    df_daily.index.name = "Report_Date"
    df_daily = df_daily.join(df_national[["Total_Production_MT", "National_Yield_Efficiency", "Season"]]).ffill()
    df_daily["Supply_YoY_Change_%"] = df_daily["Total_Production_MT"].pct_change(periods=365) * 100
    save_dataset(df_daily, PREPROCESSED_PATHS["dcs_daily"])


def run_weather_exchange() -> None:
    print("3/7 Exchange rates and weather")

    fx = pd.read_csv(RAW_PATHS["exchange_rates"])
    if "LKR=X" in fx.columns:
        fx = fx.drop(columns=["LKR=X"])
    fx = fx.rename(columns={"date": "Report_Date", "USD_LKR_Rate": "Exchange_Rate"})
    fx["Report_Date"] = pd.to_datetime(fx["Report_Date"])
    fx = fx.set_index("Report_Date").sort_index()
    fx["Exchange_Rate"] = pd.to_numeric(fx["Exchange_Rate"], errors="coerce").ffill()
    save_dataset(fx, PREPROCESSED_PATHS["exchange_daily"])

    weather = pd.read_csv(RAW_PATHS["weather"])
    weather["Report_Date"] = pd.to_datetime(weather["Report_Date"])
    weather = weather.set_index("Report_Date").sort_index()
    for col in ["Rainfall_mm", "Temp_Max_C", "Temp_Min_C"]:
        if col in weather.columns:
            weather[col] = pd.to_numeric(weather[col], errors="coerce")
    if "Rainfall_mm" in weather.columns:
        weather["Rainfall_mm"] = weather["Rainfall_mm"].fillna(0)
        weather["Rainfall_14d_Cumulative"] = weather["Rainfall_mm"].rolling(window=14, min_periods=1).sum()
    for col in ["Temp_Max_C", "Temp_Min_C"]:
        if col in weather.columns:
            weather[col] = weather[col].interpolate(method="linear")
    if "Temp_Max_C" in weather.columns:
        weather["Is_Extreme_Heat"] = np.where(weather["Temp_Max_C"] > 35.0, 1, 0)
    save_dataset(weather, PREPROCESSED_PATHS["weather_daily"])


def run_wfp() -> None:
    print("4/7 WFP market prices")
    df_wfp = pd.read_csv(RAW_PATHS["wfp_prices"])
    df_wfp["date"] = pd.to_datetime(df_wfp["date"])
    filtered = df_wfp[
        df_wfp["commodity"].isin(WFP_COMMODITIES)
        & (df_wfp["currency"] == "LKR")
        & (df_wfp["date"] >= PROJECT_START_DATE)
    ].copy()
    filtered["price"] = pd.to_numeric(filtered["price"], errors="coerce")
    pivot = filtered.pivot_table(index="date", columns=["market", "commodity"], values="price", aggfunc="mean")
    pivot.columns = [f"{market}_{commodity}" for market, commodity in pivot.columns]
    daily_idx = pd.date_range(start=PROJECT_START_DATE, end=pivot.index.max(), freq="D")
    daily = pivot.reindex(daily_idx).ffill().bfill()
    daily.index.name = "Report_Date"
    save_dataset(daily, PREPROCESSED_PATHS["wfp_daily"])


def run_faostat() -> None:
    print("5/7 FAOSTAT annual features")

    def sanitize(*parts: str) -> str:
        text = "_".join(str(part).strip() for part in parts if str(part).strip())
        text = re.sub(r"[^\w]+", "_", text)
        return re.sub(r"_+", "_", text).strip("_")

    raw_files = sorted(RAW_PATHS["faostat_dir"].glob("FAOSTAT_data_en_*.csv"))
    frames = [pd.read_csv(path, encoding="latin-1") for path in raw_files]
    raw = pd.concat(frames, ignore_index=True).drop_duplicates()
    raw = raw[raw["Year"] >= 2015].copy()
    raw["Value"] = pd.to_numeric(raw["Value"], errors="coerce")
    raw["Feature"] = raw.apply(
        lambda row: sanitize("FAO", str(row["Item"]), str(row["Element"]), str(row.get("Unit", ""))),
        axis=1,
    )
    annual = raw.pivot_table(index="Year", columns="Feature", values="Value", aggfunc="mean")
    save_dataset(annual, PREPROCESSED_PATHS["faostat_annual"])


def run_cbsl() -> None:
    print("6/7 CBSL wages and producer prices")
    required = [
        RAW_PATHS["cbsl_producer_prices"],
        RAW_PATHS["cbsl_daily_wages"],
        RAW_PATHS["cbsl_monthly_wages"],
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        print("  Skipped: CBSL Excel files not found in Raw_data/CBSL_Data/")
        for path in missing:
            print(f"    - {path.name}")
        return

    def sanitize(*parts: str) -> str:
        text = "_".join(str(part).strip() for part in parts if str(part).strip())
        text = re.sub(r"[^\w]+", "_", text)
        return re.sub(r"_+", "_", text).strip("_")

    def year_columns(header_row: pd.Series) -> list[tuple[int, int]]:
        years: list[tuple[int, int]] = []
        for col_idx in header_row.index:
            text = str(header_row[col_idx]).strip().replace("(a)", "").strip()
            try:
                year = int(float(text))
            except ValueError:
                continue
            if 2000 <= year <= 2100:
                years.append((col_idx, year))
        return years

    def extract_producer_prices(path) -> pd.DataFrame:
        raw = pd.read_excel(path, header=None)
        records = []
        in_section = False
        for _, row in raw.iterrows():
            label = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if label == "Commodity":
                in_section = True
                continue
            if in_section and label.startswith("("):
                break
            if not in_section or not label.lower().startswith("paddy"):
                continue
            for col_idx, year in year_columns(raw.iloc[3]):
                value = pd.to_numeric(row[col_idx], errors="coerce")
                if pd.notna(value):
                    records.append(
                        {
                            "Year": year,
                            "Feature": sanitize("CBSL", "Producer_Price_Paddy_LKR"),
                            "Value": value,
                        }
                    )
        return pd.DataFrame(records)

    def extract_paddy_wages(path) -> pd.DataFrame:
        raw = pd.read_excel(path, header=None)
        records = []
        in_paddy = False
        for _, row in raw.iterrows():
            activity = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            labour = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            if activity == "Paddy":
                in_paddy = True
                continue
            if in_paddy and activity.startswith("("):
                break
            if not in_paddy or labour != "M" or not activity or activity == "nan":
                continue
            for col_idx, year in year_columns(raw.iloc[3]):
                value = pd.to_numeric(row[col_idx], errors="coerce")
                if pd.notna(value):
                    records.append(
                        {
                            "Year": year,
                            "Feature": sanitize("CBSL", "Wage", activity),
                            "Value": value,
                        }
                    )
        return pd.DataFrame(records)

    def extract_monthly_wages(path) -> pd.DataFrame:
        raw = pd.read_excel(path, header=None)
        month_map = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }
        header = raw.iloc[3]
        month_cols = {
            idx: month_map[str(label).strip()]
            for idx, label in header.items()
            if str(label).strip() in month_map
        }
        records = []
        current_year = current_crop = current_activity = None
        for _, row in raw.iterrows():
            first = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            second = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            if first.startswith("Year"):
                match = re.search(r"(\d{4})", first)
                current_year = int(match.group(1)) if match else None
                continue
            if first == "Agriculture":
                continue
            if first and first != "nan":
                current_crop = first
                current_activity = None
            if second and second != "nan":
                current_activity = second
            if current_year is None or current_crop != "Paddy" or not current_activity:
                continue
            for col_idx, month in month_cols.items():
                value = pd.to_numeric(row[col_idx], errors="coerce")
                if pd.notna(value):
                    records.append(
                        {
                            "Year": current_year,
                            "Month": month,
                            "Feature": sanitize("CBSL", "MonthlyWage", current_crop, current_activity),
                            "Value": value,
                        }
                    )
        monthly = pd.DataFrame(records)
        if monthly.empty:
            return monthly
        monthly["YearMonth"] = pd.to_datetime(
            monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str) + "-01"
        )
        return monthly.sort_values("YearMonth").groupby(["Year", "Feature"], as_index=False)["Value"].last()

    producer = extract_producer_prices(RAW_PATHS["cbsl_producer_prices"])
    wages = extract_paddy_wages(RAW_PATHS["cbsl_daily_wages"])
    monthly = extract_monthly_wages(RAW_PATHS["cbsl_monthly_wages"])
    combined = pd.concat([producer, wages, monthly], ignore_index=True)
    annual = combined.pivot_table(index="Year", columns="Feature", values="Value", aggfunc="mean")
    save_dataset(annual, PREPROCESSED_PATHS["cbsl_annual"])


def main() -> None:
    run_harti()
    run_dcs()
    run_weather_exchange()
    run_wfp()
    run_faostat()
    run_cbsl()
    print("7/8 Integrating datasets")
    final = build_final_dataset()
    print(f"Saved: {PREPROCESSED_PATHS['final_integrated']}")
    print(f"Shape: {final.shape}")
    print(f"Date range: {final.index.min().date()} to {final.index.max().date()}")

    print("8/8 Rice price volatility preprocessing")
    run_volatility_preprocessing()


if __name__ == "__main__":
    main()
