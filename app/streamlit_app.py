"""
app/streamlit_app.py — Streamlit web UI for lseg-data-validator.

This module is intentionally thin: all business logic lives in lseg_validator/.
This file only handles file upload, rendering, and layout.

Run with::

    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from lseg_validator import DataQualityReport
from lseg_validator.checks.schema_diff import run_all as schema_diff

st.set_page_config(page_title="LSEG Data Validator", layout="wide")
st.title("LSEG Data Validator")
st.caption("Drag-and-drop your LSEG CSV snapshot to run quality checks instantly.")

# ── File upload ──────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    file_a = st.file_uploader("Primary snapshot (required)", type=["csv", "parquet"])
with col_b:
    file_b = st.file_uploader(
        "Comparison snapshot (optional, for diff)", type=["csv", "parquet"]
    )


def _load(uploaded) -> pd.DataFrame:
    """Parse an uploaded file into a DataFrame."""
    if uploaded.name.endswith(".parquet"):
        return pd.read_parquet(uploaded)
    return pd.read_csv(uploaded)


if file_a is None:
    st.info("Upload a CSV or Parquet file to begin.")
    st.stop()

df = _load(file_a)
report = DataQualityReport(df)
results = report.to_dict()

st.subheader(f"Dataset: `{file_a.name}` — {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── Completeness tab ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["Completeness", "Consistency", "Anomalies", "Schema Diff"]
)

with tab1:
    null_rates = results["completeness"]["null_rate_per_column"]
    severity = results["completeness"]["null_severity"]
    null_df = pd.DataFrame(
        {
            "Column": list(null_rates.keys()),
            "Null Rate (%)": [v * 100 for v in null_rates.values()],
            "Severity": [severity.get(c, "low") for c in null_rates],
        }
    )
    st.dataframe(null_df, use_container_width=True)

    if null_rates:
        fig = px.bar(
            null_df,
            x="Column",
            y="Null Rate (%)",
            color="Severity",
            color_discrete_map={"low": "green", "medium": "orange", "high": "red"},
            title="Null Rate per Column",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    c = results["consistency"]
    st.metric("Numeric-string columns", len(c["numeric_string_columns"]))
    st.metric("Invalid RIC codes", c["invalid_ric_count"])
    st.metric("Duplicate rows", c["duplicate_row_count"])
    if c["numeric_string_columns"]:
        st.warning(
            f"Columns stored as strings but appear numeric: {c['numeric_string_columns']}"
        )

with tab3:
    a = results["anomaly"]
    rows = []
    for col, idxs in a["zscore_outliers"].items():
        rows.append({"Column": col, "Method": "Z-score", "Outlier count": len(idxs)})
    for col, idxs in a["iqr_outliers"].items():
        rows.append({"Column": col, "Method": "IQR", "Outlier count": len(idxs)})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.success("No anomalies detected.")

with tab4:
    if file_b is None:
        st.info("Upload a second snapshot to see schema diff.")
    else:
        df_b = _load(file_b)
        diff_result = schema_diff(df, df_b)
        st.json(diff_result)

# ── Download HTML report ─────────────────────────────────────────────────────
st.divider()
html = report.to_html()
st.download_button(
    label="Download HTML Report",
    data=html.encode(),
    file_name="lseg_quality_report.html",
    mime="text/html",
)
