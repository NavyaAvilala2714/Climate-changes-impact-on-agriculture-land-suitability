# Interpretable Classification (Random Forest)

This package implements the **Interpretable Classification (Random Forest)** model used for cropland suitability prediction, as described in the **Methodology** (section 3) and **ML Insights** page.

## What it does

- **Model:** `sklearn.ensemble.RandomForestRegressor` — predicts suitability score (0–100) from:
  - `region_id`, `scenario_id`
  - `time_period_future` (0 = current, 1 = future)
  - `co2_level_ppm` (from scenario)
  - `latitude`, `longitude` (from region coordinates)

- **Interpretability:** The model exposes **feature importance** (`model.feature_importances_`), so we can show which inputs (e.g. CO₂ level, time period, location) drive each prediction.

## Files

- **`random_forest_model.py`** — Trains the model on DB data, exposes `get_feature_importance()` and `train_interpretable_model(training_rows)`.
- **`__init__.py`** — Re-exports for use in `main.py`.

## Usage

Training runs at app startup in `main.py` after the DB is seeded. The API endpoint **GET /api/ml/feature-importance** returns the model name and feature importance; the frontend **ML Insights** page fetches and displays it.
