"""SQLAlchemy models matching the frontend schema (regions, scenarios, suitability_predictions)."""
from sqlalchemy import Column, Integer, Text, ForeignKey, JSON
from database import Base


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    coordinates = Column(JSON, nullable=True)  # e.g. {"lat": 48.0, "lng": 66.0}


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    co2_level = Column(Integer, nullable=False)


class SuitabilityPrediction(Base):
    __tablename__ = "suitability_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    time_period = Column(Text, nullable=False)  # "current" | "future"
    suitability_class = Column(Text, nullable=False)
    suitability_score = Column(Integer, nullable=False)
    factors = Column(JSON, nullable=False)  # { temperature, rainfall, soilQuality, irrigation }
    risks = Column(JSON, nullable=False)  # { degradation, waterStress, foodSecurity }
