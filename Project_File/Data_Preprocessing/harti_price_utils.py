from __future__ import annotations

import pandas as pd

FIFTY_KG_THRESHOLD = 1000
GRAY_ZONE_MIN = 500
KG_BAG_DIVISOR = 50


def coalesce_price_columns(df: pd.DataFrame, current_col: str, previous_col: str, out_col: str) -> pd.DataFrame:
    out = df.copy()
    out[out_col] = pd.to_numeric(out[current_col], errors="coerce")
    out[out_col] = out[out_col].fillna(pd.to_numeric(out[previous_col], errors="coerce"))
    return out


def convert_to_price_per_kg(value, prev_value=None, next_value=None) -> tuple[float, bool]:
    if pd.isna(value):
        return value, False

    if value >= FIFTY_KG_THRESHOLD:
        return value / KG_BAG_DIVISOR, True

    if value >= GRAY_ZONE_MIN:
        neighbors = [v for v in (prev_value, next_value) if v is not None and not pd.isna(v)]
        if any(v >= FIFTY_KG_THRESHOLD for v in neighbors):
            return value / KG_BAG_DIVISOR, True

    return value, False


def convert_long_prices(df: pd.DataFrame, price_col: str, market: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = df.sort_values(["Item", "Report_Date"]).copy()
    converted_prices = pd.Series(index=work.index, dtype=float)
    logs = []

    for item in work["Item"].unique():
        item_mask = work["Item"] == item
        item_idx = work.index[item_mask]
        values = work.loc[item_mask, price_col].tolist()

        for i, row_idx in enumerate(item_idx):
            value = values[i]
            if pd.isna(value):
                converted_prices.loc[row_idx] = pd.NA
                continue

            prev_value = values[i - 1] if i > 0 else None
            next_value = values[i + 1] if i + 1 < len(values) else None
            new_value, changed = convert_to_price_per_kg(value, prev_value, next_value)
            converted_prices.loc[row_idx] = new_value

            if changed:
                logs.append(
                    {
                        "Report_Date": work.at[row_idx, "Report_Date"],
                        "Original_Price": value,
                        "Converted_Price_per_kg": new_value,
                        "Item": item,
                        "Market": market,
                    }
                )

    work[f"{price_col}_per_kg"] = converted_prices
    return work, pd.DataFrame(logs)


def preprocess_harti_prices(long_df: pd.DataFrame, price_col: str, market: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    converted_long, log_df = convert_long_prices(long_df, price_col, market)

    wide = converted_long.pivot_table(
        index="Report_Date",
        columns="Item",
        values=f"{price_col}_per_kg",
        aggfunc="median",
    ).sort_index()
    wide.index.name = "Report_Date"

    long_out = converted_long[
        ["Report_Date", "Item", price_col, f"{price_col}_per_kg"]
    ].rename(columns={price_col: "Original_Price", f"{price_col}_per_kg": "Price_per_kg"})
    long_out["Market"] = market

    return wide, long_out, log_df
