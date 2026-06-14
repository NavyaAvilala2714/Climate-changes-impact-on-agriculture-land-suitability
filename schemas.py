"""Pydantic schemas for API responses. Use camelCase so the React frontend receives expected keys."""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict


class RegionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    description: str
    coordinates: dict[str, Any] | None = None


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    description: str
    co2_level: int

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["co2Level"] = data.pop("co2_level")
        return data


class FactorsSchema(BaseModel):
    temperature: int
    rainfall: int
    soilQuality: int
    irrigation: int


class RisksSchema(BaseModel):
    degradation: Literal["Low", "Medium", "High"]
    waterStress: Literal["Low", "Medium", "High"]
    foodSecurity: Literal["Low", "Medium", "High"]


class PredictionResponse(BaseModel):
    """Single prediction row; for /api/analysis/predict we embed region and scenario."""
    id: int
    region_id: int
    scenario_id: int
    time_period: str
    suitability_class: str
    suitability_score: int
    factors: dict[str, int]  # temperature, rainfall, soilQuality, irrigation
    risks: dict[str, str]    # degradation, waterStress, foodSecurity

    def to_camel_dict(self) -> dict:
        return {
            "id": self.id,
            "regionId": self.region_id,
            "scenarioId": self.scenario_id,
            "timePeriod": self.time_period,
            "suitabilityClass": self.suitability_class,
            "suitabilityScore": self.suitability_score,
            "factors": self.factors,
            "risks": self.risks,
        }


class SimulationResponse(BaseModel):
    """Predict endpoint: prediction + region + scenario (camelCase for frontend)."""
    id: int
    regionId: int
    scenarioId: int
    timePeriod: str
    suitabilityClass: str
    suitabilityScore: int
    factors: dict[str, int]
    risks: dict[str, str]
    region: dict  # RegionResponse as dict with id, name, description, coordinates
    scenario: dict  # ScenarioResponse as dict with id, name, description, co2Level
