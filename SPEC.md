# lseg-data-validator — Project Spec

## Purpose
A free, open-source data quality toolkit purpose-built for developers using the
LSEG Data Library for Python (`lseg-data`). It takes a pandas DataFrame returned
by any `lseg-data` API call and produces a rich quality report: null rates, type
inference, anomaly detection, and schema drift between two time periods.

Target audience: quant developers, financial coders, and data scientists who use
LSEG Workspace / RDP APIs and want fast confidence checks on the data they pull.

---

## Core Features (MVP — 1-2 weeks)

### 1. CLI tool (`lseg-validator`)
- `lseg-validator check <file.csv>` — run quality checks on a CSV/parquet snapshot
- `lseg-validator diff <file_a.csv> <file_b.csv>` — compare two snapshots for schema drift
- `lseg-validator report <file.csv> --output report.html` — generate standalone HTML report
- Outputs: coloured terminal summary + optional HTML report

### 2. Python API (importable)
```python
from lseg_validator import DataQualityReport
report = DataQualityReport(df)
report.summary()       # prints to terminal
report.to_html()       # returns HTML string
report.to_dict()       # returns structured dict for programmatic use
```

### 3. Streamlit Web UI (`streamlit run app.py`)
- Drag-and-drop CSV/parquet upload
- Auto-detect LSEG field naming conventions (TR.* fields, RIC codes, timestamps)
- Visual null heatmap (seaborn or plotly)
- Field distribution charts (histogram per numeric column)
- Anomaly flags table (Z-score > 3 or IQR outliers, per column)
- Schema diff view (side-by-side when two files uploaded)
- One-click HTML report download

---

## Quality Check Modules

### Completeness
- Null rate per column (% missing)
- Null rate over time (if timestamp column detected) — catches data feed outages
- Flag columns with >10%, >25%, >50% nulls with severity levels

### Consistency
- Type inference — detect columns that are numeric but stored as strings
- Date/timestamp parsing — detect malformed LSEG timestamps
- RIC code format validation (basic regex: alphanumeric + `.` + exchange suffix)
- Duplicate row detection

### Anomaly Detection
- Z-score outlier flagging (threshold configurable, default: |z| > 3)
- IQR outlier flagging (default: 1.5x IQR)
- Sudden value spikes (% change > configurable threshold between consecutive rows)

### Schema Drift (diff mode)
- New columns added
- Columns removed
- Data type changes per column
- Null rate delta per column (> 5% change flagged)
- Value range shifts (mean/std delta)

---

## Tech Stack
- Python 3.10+
- pandas, numpy — core data handling
- scipy — Z-score, IQR stats
- plotly — interactive charts in Streamlit
- streamlit — web UI
- typer — CLI framework
- jinja2 — HTML report templating
- pytest — tests
- black + ruff — formatting/linting

No LSEG credentials required to run — works on any pandas DataFrame or CSV file.
Include sample data fixtures from LSEG's public GitHub examples for demo/testing.

---

## Sample Data Strategy (no credentials needed)
Pull sample CSV fixtures from LSEG's public GitHub:
- https://github.com/LSEG-API-Samples/Example.DataLibrary.Python
Use these as test fixtures AND as demo data in the Streamlit app.
Synthetic data generator for CI: generate realistic LSEG-shaped DataFrames
with known quality issues injected (nulls, outliers, type mismatches).

---

## Project Structure
```
lseg-data-validator/
├── CLAUDE.md
├── SPEC.md
├── README.md                  ← primary visibility asset
├── pyproject.toml
├── lseg_validator/
│   ├── __init__.py
│   ├── checks/
│   │   ├── completeness.py
│   │   ├── consistency.py
│   │   ├── anomaly.py
│   │   └── schema_diff.py
│   ├── report.py              ← DataQualityReport class
│   ├── cli.py                 ← typer CLI
│   └── templates/
│       └── report.html.j2     ← Jinja2 HTML report template
├── app/
│   └── streamlit_app.py       ← Streamlit UI
├── tests/
│   ├── fixtures/              ← sample CSVs from LSEG public GitHub
│   ├── test_completeness.py
│   ├── test_anomaly.py
│   └── test_schema_diff.py
└── docs/
    └── lseg-field-reference.md ← TR.* field naming conventions doc
```

---

## Phased Build Plan

### Phase 1 — Core engine (Days 1–3)
- Scaffold project with pyproject.toml, ruff, black, pytest
- Implement completeness.py, consistency.py, anomaly.py
- Write tests against synthetic fixtures
- DataQualityReport class with .summary() and .to_dict()

### Phase 2 — CLI + HTML report (Days 4–6)
- typer CLI: check, diff, report commands
- Jinja2 HTML report template (clean, professional design)
- schema_diff.py module
- Full test coverage

### Phase 3 — Streamlit UI (Days 7–9)
- File upload + auto field detection
- Plotly null heatmap + distribution charts
- Anomaly flags table
- Schema diff side-by-side view
- Download report button

### Phase 4 — Polish + Launch (Days 10–14)
- README with LSEG-specific framing, badges, screenshots/GIF
- Deploy Streamlit app to Streamlit Cloud (free)
- Post to LSEG developer community forum
- LinkedIn post series (3 posts)

---

## README Strategy (visibility)
The README is a primary SEO + community asset. It must:
- Open with the exact problem statement LSEG devs hit ("You pulled data from RDP.
  Is it actually clean?")
- Show a 2-minute demo GIF at the top
- Include a "Works with" section listing lseg-data sessions:
  Desktop, Platform, CodeBook, Workspace
- Include sample output showing real LSEG field names (TR.PriceClose, RIC, etc.)
- Link to LSEG Developer Community and their GitHub org

---

## LinkedIn Post Plan
Post 1 (Day 1): "I spent a week reading the LSEG developer forums. Here's the
#1 pain point I found that nobody has solved yet." (hook post, no code yet)

Post 2 (Day 7): "Here's what I built to solve it — first look at
lseg-data-validator." (show the Streamlit UI, share GitHub link)

Post 3 (Day 14): "Lessons learned building a dev tool for the LSEG ecosystem
from scratch, with no credentials." (technical storytelling, tags LSEG)
