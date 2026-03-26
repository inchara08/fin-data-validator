# CLAUDE.md — lseg-data-validator

## Project
Open-source Python data quality toolkit for LSEG Data Library outputs.
See SPEC.md for full feature spec and phased build plan.

## Stack
- Python 3.10+, pandas, numpy, scipy, plotly, streamlit, typer, jinja2
- Tests: pytest (run with `pytest tests/`)
- Format: `black .` then `ruff check .`
- Package: pyproject.toml (no setup.py)

## Structure
- `lseg_validator/checks/` — individual quality check modules (one concern each)
- `lseg_validator/report.py` — DataQualityReport class, composes all checks
- `lseg_validator/cli.py` — typer CLI entry point
- `app/streamlit_app.py` — Streamlit UI (import from lseg_validator, no logic here)
- `tests/fixtures/` — sample CSVs, never require live LSEG credentials

## Key rules
- No LSEG credentials ever required — all code runs on local CSV/parquet/DataFrame
- Each check module must work standalone: takes a DataFrame, returns a typed dict
- Keep Streamlit app thin — all logic lives in lseg_validator/, app just renders
- Never hardcode thresholds — expose them as parameters with sensible defaults
- All public functions must have docstrings

## Commands
- Run tests: `pytest tests/ -v`
- Format: `black . && ruff check .`
- Run CLI: `python -m lseg_validator.cli check <file>`
- Run UI: `streamlit run app/streamlit_app.py`
