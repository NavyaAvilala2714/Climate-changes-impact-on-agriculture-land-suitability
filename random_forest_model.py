"""
Interpretable Classification (Random Forest) for Land Suitability.

We use a Random Forest Regressor to predict cropland suitability score (0-100)
from climate and region features. The model is interpretable: feature_importance_
shows which inputs (CO2 level, time period, latitude, etc.) drive each prediction.

References: Methodology (section 3), ML Insights page.
"""
from typing import Any, Optional

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np

# Module-level trained model and metadata (set by train_interpretable_model)
_model: Optional[RandomForestRegressor] = None
_feature_names: list[str] = []
_training_score: Optional[float] = None

# Feature names used for interpretability (must match build_training_data)
FEATURE_NAMES = [
    "region_id",
    "scenario_id",
    "time_period_future",  # 0 = current, 1 = future
    "co2_level_ppm",
    "latitude",
    "longitude",
]


def _build_training_data(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    """
    Build X (features) and y (suitability score) from DB rows.
    Each row has: region_id, scenario_id, time_period, co2_level, lat, lng, suitability_score.
    """
    X_list = []
    y_list = []
    for r in rows:
        time_future = 1 if (r.get("time_period") or "").strip().lower() == "future" else 0
        coords = r.get("coordinates") or {}
        lat = float(coords.get("lat", 0))
        lng = float(coords.get("lng", 0))
        X_list.append([
            r["region_id"],
            r["scenario_id"],
            time_future,
            r["co2_level"],
            lat,
            lng,
        ])
        y_list.append(r["suitability_score"])
    return np.array(X_list, dtype=np.float64), np.array(y_list, dtype=np.float64)


def train_interpretable_model(training_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Train the Interpretable Classification (Random Forest) model on suitability data.

    training_rows: list of dicts with region_id, scenario_id, time_period, co2_level,
                   coordinates (lat, lng), suitability_score.

    Returns summary dict with n_samples, train_r2, feature_importance.
    """
    global _model, _feature_names, _training_score

    if not training_rows:
        return {"error": "No training data", "n_samples": 0}

    X, y = _build_training_data(training_rows)
    _feature_names = FEATURE_NAMES.copy()

    # Train/test split for reporting; we train on full data for production use
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X_train, y_train)
    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)

    # Retrain on full dataset for API use
    _model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
    )
    _model.fit(X, y)
    _training_score = float(_model.score(X, y))

    return {
        "model": "RandomForestRegressor",
        "n_samples": len(y),
        "train_r2": round(float(train_r2), 4),
        "test_r2": round(float(test_r2), 4),
        "feature_importance": dict(zip(_feature_names, _model.feature_importances_.tolist())),
    }


def is_trained() -> bool:
    """Return True if the interpretable model has been trained."""
    return _model is not None


def get_feature_importance() -> dict[str, Any]:
    """
    Return feature names and importance for the trained Random Forest.
    Used by the Insights page and /api/ml/feature-importance.
    """
    if _model is None:
        return {
            "model": "Interpretable Classification (Random Forest)",
            "trained": False,
            "feature_importance": {},
            "feature_names": FEATURE_NAMES,
        }
    importance = dict(zip(_feature_names, _model.feature_importances_.tolist()))
    # Sort by importance descending for display
    sorted_importance = dict(
        sorted(importance.items(), key=lambda x: x[1], reverse=True)
    )
    return {
        "model": "Interpretable Classification (Random Forest)",
        "trained": True,
        "feature_names": _feature_names,
        "feature_importance": sorted_importance,
        "training_r2": _training_score,
    }
