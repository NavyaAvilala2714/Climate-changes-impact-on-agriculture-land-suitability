"""
FastAPI backend for Climate Change Land Suitability.
API shape matches the existing React frontend (camelCase where expected).
Uses Interpretable Classification (Random Forest) in backend/ml/ for feature importance.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import Region, Scenario, SuitabilityPrediction
from seed import seed
from ml.random_forest_model import train_interpretable_model, get_feature_importance


def _build_ml_training_data(db: Session) -> list[dict]:
    """Build training rows for Interpretable Classification (Random Forest) from DB."""
    predictions = db.query(SuitabilityPrediction).all()
    regions = {r.id: r for r in db.query(Region).all()}
    scenarios = {s.id: s for s in db.query(Scenario).all()}
    rows = []
    for p in predictions:
        r = regions.get(p.region_id)
        s = scenarios.get(p.scenario_id)
        if not r or not s:
            continue
        coords = r.coordinates or {}
        rows.append({
            "region_id": p.region_id,
            "scenario_id": p.scenario_id,
            "time_period": p.time_period,
            "co2_level": s.co2_level,
            "coordinates": coords,
            "suitability_score": p.suitability_score,
        })
    return rows


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = next(get_db())
    try:
        seed(db)
        # Train Interpretable Classification (Random Forest) on suitability data
        training_rows = _build_ml_training_data(db)
        if training_rows:
            result = train_interpretable_model(training_rows)
            print(f"ML: {result.get('model')} trained on {result.get('n_samples')} samples, R²={result.get('train_r2')}")
    finally:
        db.close()
    yield


app = FastAPI(title="Climate Land Suitability API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Helpers: ORM -> JSON (camelCase for frontend) ----

def region_to_dict(r: Region) -> dict:
    return {"id": r.id, "name": r.name, "description": r.description, "coordinates": r.coordinates}


def scenario_to_dict(s: Scenario) -> dict:
    return {"id": s.id, "name": s.name, "description": s.description, "co2Level": s.co2_level}


def prediction_to_camel(p: SuitabilityPrediction) -> dict:
    return {
        "id": p.id,
        "regionId": p.region_id,
        "scenarioId": p.scenario_id,
        "timePeriod": p.time_period,
        "suitabilityClass": p.suitability_class,
        "suitabilityScore": p.suitability_score,
        "factors": p.factors,
        "risks": p.risks,
    }


# ---- Routes ----

@app.get("/api/regions")
def list_regions(db: Session = Depends(get_db)):
    """List all regions."""
    regions = db.query(Region).all()
    return [region_to_dict(r) for r in regions]


@app.get("/api/regions/{region_id:int}")
def get_region(region_id: int, db: Session = Depends(get_db)):
    """Get one region by id."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail={"message": "Region not found"})
    return region_to_dict(region)


@app.get("/api/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    """List all climate scenarios."""
    scenarios = db.query(Scenario).all()
    return [scenario_to_dict(s) for s in scenarios]


@app.get("/api/analysis/predict")
def predict(
    regionId: int = Query(..., alias="regionId"),
    scenarioId: int = Query(..., alias="scenarioId"),
    timePeriod: str = Query(..., alias="timePeriod"),
    db: Session = Depends(get_db),
):
    """
    Get suitability prediction for region + scenario + time period.
    Returns prediction with nested region and scenario (SimulationResponse).
    """
    if timePeriod not in ("current", "future"):
        raise HTTPException(status_code=400, detail={"message": "Invalid query parameters"})

    pred = (
        db.query(SuitabilityPrediction)
        .filter(
            SuitabilityPrediction.region_id == regionId,
            SuitabilityPrediction.scenario_id == scenarioId,
            SuitabilityPrediction.time_period == timePeriod,
        )
        .first()
    )
    if not pred:
        raise HTTPException(
            status_code=404,
            detail={"message": "Prediction data not available for this combination"},
        )

    region = db.query(Region).filter(Region.id == pred.region_id).first()
    scenario = db.query(Scenario).filter(Scenario.id == pred.scenario_id).first()
    if not region or not scenario:
        raise HTTPException(status_code=500, detail={"message": "Internal server error"})

    response = prediction_to_camel(pred)
    response["region"] = region_to_dict(region)
    response["scenario"] = scenario_to_dict(scenario)
    return response


# ---- Interpretable ML (Random Forest) ----

@app.get("/api/ml/feature-importance")
def ml_feature_importance():
    """
    Return feature importance from the Interpretable Classification (Random Forest) model.
    Used by the ML Insights page to show which drivers (CO2, time period, location) shape suitability.
    """
    return get_feature_importance()
