"""
tests/fixtures/generate.py — synthetic LSEG-shaped DataFrame generator.

Creates realistic DataFrames that mimic data returned by the LSEG Data Library
for Python.  Supports two modes:

- **clean**: no quality issues injected.
- **dirty**: quality issues injected — nulls, outliers, type mismatches,
  and a duplicate row.

Usage (CLI)::

    python tests/fixtures/generate.py

This writes ``sample_clean.csv`` and ``sample_dirty.csv`` into the same
``tests/fixtures/`` directory.

Usage (import)::

    from tests.fixtures.generate import make_clean_df, make_dirty_df
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────

RICS = [
    "MSFT.O",
    "AAPL.O",
    "LSEG.L",
    "BP.L",
    "TSLA.O",
    "AMZN.O",
    "SHEL.L",
    "NVDA.O",
    "AZN.L",
    "GOOGL.O",
]

N_ROWS = 100
SEED = 42

# ── Helpers ───────────────────────────────────────────────────────────────────


def _base_df(n: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Generate a clean base DataFrame with realistic LSEG-shaped data."""
    rng = np.random.default_rng(seed)

    dates = pd.date_range("2024-01-02", periods=n, freq="B")  # business days
    rics = [RICS[i % len(RICS)] for i in range(n)]

    close = rng.uniform(50.0, 500.0, size=n).round(4)
    high = (close + rng.uniform(0.5, 5.0, size=n)).round(4)
    low = (close - rng.uniform(0.5, 5.0, size=n)).round(4)
    volume = rng.integers(100_000, 10_000_000, size=n).astype(float)

    return pd.DataFrame(
        {
            "RIC": rics,
            "Timestamp": dates.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "TR.PriceClose": close,
            "TR.PriceHigh": high,
            "TR.PriceLow": low,
            "TR.Volume": volume,
        }
    )


# ── Public API ────────────────────────────────────────────────────────────────


def make_clean_df(n: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Return a clean LSEG-shaped DataFrame with no quality issues.

    Parameters
    ----------
    n:
        Number of rows.
    seed:
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
    """
    return _base_df(n=n, seed=seed)


def make_dirty_df(n: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Return a dirty LSEG-shaped DataFrame with injected quality issues.

    Issues injected
    ---------------
    1. ~15 % nulls in ``TR.Volume`` (~15 rows set to NaN).
    2. 3 outlier prices in ``TR.PriceClose`` (values ~10× the mean).
    3. 2 type mismatches: rows 5 and 6 have ``TR.PriceClose`` stored as a string.
    4. 1 duplicate row (row 0 duplicated at the end).

    Parameters
    ----------
    n:
        Number of rows.
    seed:
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
    """
    rng = np.random.default_rng(seed)
    df = _base_df(n=n, seed=seed)

    # 1. ~15 % nulls in TR.Volume
    null_indices = rng.choice(n, size=max(1, int(n * 0.15)), replace=False)
    df.loc[null_indices, "TR.Volume"] = np.nan

    # 2. 3 outliers in TR.PriceClose
    mean_price = df["TR.PriceClose"].mean()
    outlier_indices = rng.choice(n, size=3, replace=False)
    df.loc[outlier_indices, "TR.PriceClose"] = (mean_price * 10).round(4)

    # 3. 2 type mismatches: TR.PriceClose stored as string for rows 5 and 6
    # Convert the whole column to object so mixed types are possible
    df["TR.PriceClose"] = df["TR.PriceClose"].astype(object)
    df.loc[5, "TR.PriceClose"] = "not_a_price"
    df.loc[6, "TR.PriceClose"] = "N/A"

    # 4. 1 duplicate row (append copy of row 0)
    duplicate = df.iloc[[0]].copy()
    df = pd.concat([df, duplicate], ignore_index=True)

    return df


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    fixtures_dir = Path(__file__).parent

    clean = make_clean_df()
    dirty = make_dirty_df()

    clean_path = fixtures_dir / "sample_clean.csv"
    dirty_path = fixtures_dir / "sample_dirty.csv"

    clean.to_csv(clean_path, index=False)
    dirty.to_csv(dirty_path, index=False)

    print(f"Written {len(clean)} rows → {clean_path}")
    print(f"Written {len(dirty)} rows → {dirty_path}")
