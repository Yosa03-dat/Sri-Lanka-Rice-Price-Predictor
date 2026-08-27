"""Execute rice_price_volatility_preprocessing.ipynb code cells."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")


def run_volatility_preprocessing() -> None:
    notebook_path = Path(__file__).resolve().parent / "rice_price_volatility_preprocessing.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace: dict = {"__name__": "__main__"}

    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        exec(compile(source, f"{notebook_path.name}:cell_{index}", "exec"), namespace)

    print("Volatility preprocessing complete.")


if __name__ == "__main__":
    run_volatility_preprocessing()
