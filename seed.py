"""Seed database with regions, scenarios, and suitability predictions.
Uses research-informed regional differences: tropics/subtropics more vulnerable under RCP 8.5."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Region, Scenario, SuitabilityPrediction


# New regions to add (when backfilling from 2 to 10 regions). Each: (name, description, lat, lng).
EXTRA_REGIONS = [
    ("South Asia", "India, Pakistan, Bangladesh — high exposure to heat stress and monsoon variability; among the most vulnerable agricultural hotspots (IPCC AR6).", 20.0, 77.0),
    ("Southeast Asia", "Vietnam, Thailand, Indonesia — rice-dependent; tropical suitability declines under high emissions; irrigation and sea-level risks.", 10.0, 106.0),
    ("East Africa", "Kenya, Tanzania, Ethiopia — mixed rainfed agriculture; drought and variability; limited adaptive capacity.", -2.0, 38.0),
    ("West Africa", "Sahel, Nigeria, Ghana — dryland cropping; high water stress; severe under RCP 8.5.", 10.0, -5.0),
    ("Southern South America", "Argentina, Chile, Uruguay — temperate cereals and soy; moderate decline under high emissions.", -32.0, -64.0),
    ("Eastern Europe", "Ukraine, Moldova, Romania — major wheat/maize producer; warming and drought risk under RCP 8.5.", 48.0, 31.0),
    ("North America Midwest", "US Corn Belt — high current suitability; resilient but not immune to future heat and water stress.", 42.0, -93.0),
    ("East Asia", "North China Plain — rice and wheat; irrigation-dependent; water stress and heat under high emissions.", 35.0, 105.0),
]

# Per-region prediction data: (suitability_class, score, factors dict, risks dict) for (current_low, current_high, future_low, future_high).
# Order matches: region 1 Central Eurasia, 2 Sub-Saharan Africa, 3 South Asia, 4 Southeast Asia, 5 East Africa, 6 West Africa, 7 Southern South America, 8 Eastern Europe, 9 North America Midwest, 10 East Asia.
REGION_PREDICTIONS = [
    # 1. Central Eurasia
    [
        ("Suitable", 85, {"temperature": 80, "rainfall": 75, "soilQuality": 90, "irrigation": 85}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 82, {"temperature": 78, "rainfall": 74, "soilQuality": 90, "irrigation": 82}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 80, {"temperature": 75, "rainfall": 70, "soilQuality": 88, "irrigation": 80}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Moderately Suitable", 55, {"temperature": 40, "rainfall": 30, "soilQuality": 70, "irrigation": 40}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
    ],
    # 2. Sub-Saharan Africa
    [
        ("Moderately Suitable", 58, {"temperature": 55, "rainfall": 50, "soilQuality": 62, "irrigation": 55}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 48, {"temperature": 45, "rainfall": 40, "soilQuality": 55, "irrigation": 35}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 60, {"temperature": 50, "rainfall": 55, "soilQuality": 60, "irrigation": 50}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Unsuitable", 25, {"temperature": 20, "rainfall": 15, "soilQuality": 40, "irrigation": 10}, {"degradation": "High", "waterStress": "High", "foodSecurity": "High"}),
    ],
    # 3. South Asia
    [
        ("Suitable", 72, {"temperature": 68, "rainfall": 70, "soilQuality": 75, "irrigation": 72}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Moderately Suitable", 68, {"temperature": 62, "rainfall": 65, "soilQuality": 72, "irrigation": 65}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 65, {"temperature": 58, "rainfall": 60, "soilQuality": 70, "irrigation": 60}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 38, {"temperature": 32, "rainfall": 28, "soilQuality": 52, "irrigation": 25}, {"degradation": "High", "waterStress": "High", "foodSecurity": "High"}),
    ],
    # 4. Southeast Asia
    [
        ("Suitable", 75, {"temperature": 72, "rainfall": 82, "soilQuality": 78, "irrigation": 70}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 70, {"temperature": 66, "rainfall": 76, "soilQuality": 74, "irrigation": 65}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Suitable", 68, {"temperature": 62, "rainfall": 72, "soilQuality": 72, "irrigation": 62}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 42, {"temperature": 35, "rainfall": 38, "soilQuality": 55, "irrigation": 30}, {"degradation": "High", "waterStress": "High", "foodSecurity": "High"}),
    ],
    # 5. East Africa
    [
        ("Moderately Suitable", 62, {"temperature": 58, "rainfall": 55, "soilQuality": 68, "irrigation": 52}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 55, {"temperature": 50, "rainfall": 48, "soilQuality": 62, "irrigation": 42}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 58, {"temperature": 52, "rainfall": 52, "soilQuality": 64, "irrigation": 48}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 32, {"temperature": 25, "rainfall": 22, "soilQuality": 45, "irrigation": 18}, {"degradation": "High", "waterStress": "High", "foodSecurity": "High"}),
    ],
    # 6. West Africa
    [
        ("Moderately Suitable", 52, {"temperature": 48, "rainfall": 45, "soilQuality": 58, "irrigation": 42}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 45, {"temperature": 40, "rainfall": 38, "soilQuality": 52, "irrigation": 32}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "High"}),
        ("Moderately Suitable", 48, {"temperature": 42, "rainfall": 42, "soilQuality": 54, "irrigation": 38}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
        ("Unsuitable", 22, {"temperature": 18, "rainfall": 15, "soilQuality": 38, "irrigation": 12}, {"degradation": "High", "waterStress": "High", "foodSecurity": "High"}),
    ],
    # 7. Southern South America
    [
        ("Suitable", 78, {"temperature": 74, "rainfall": 76, "soilQuality": 82, "irrigation": 78}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 74, {"temperature": 70, "rainfall": 72, "soilQuality": 78, "irrigation": 72}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Suitable", 72, {"temperature": 66, "rainfall": 68, "soilQuality": 76, "irrigation": 68}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Moderately Suitable", 50, {"temperature": 42, "rainfall": 40, "soilQuality": 62, "irrigation": 38}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
    ],
    # 8. Eastern Europe
    [
        ("Suitable", 82, {"temperature": 78, "rainfall": 76, "soilQuality": 88, "irrigation": 80}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 78, {"temperature": 72, "rainfall": 70, "soilQuality": 84, "irrigation": 74}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Suitable", 75, {"temperature": 68, "rainfall": 66, "soilQuality": 80, "irrigation": 70}, {"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Moderately Suitable", 58, {"temperature": 48, "rainfall": 42, "soilQuality": 68, "irrigation": 45}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
    ],
    # 9. North America Midwest
    [
        ("Suitable", 88, {"temperature": 84, "rainfall": 82, "soilQuality": 92, "irrigation": 86}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 85, {"temperature": 80, "rainfall": 78, "soilQuality": 90, "irrigation": 82}, {"degradation": "Low", "waterStress": "Low", "foodSecurity": "Low"}),
        ("Suitable", 82, {"temperature": 76, "rainfall": 74, "soilQuality": 88, "irrigation": 78}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Moderately Suitable", 62, {"temperature": 52, "rainfall": 48, "soilQuality": 72, "irrigation": 50}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
    ],
    # 10. East Asia
    [
        ("Suitable", 80, {"temperature": 75, "rainfall": 78, "soilQuality": 82, "irrigation": 82}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Suitable", 76, {"temperature": 70, "rainfall": 72, "soilQuality": 78, "irrigation": 76}, {"degradation": "Low", "waterStress": "Medium", "foodSecurity": "Low"}),
        ("Suitable", 72, {"temperature": 66, "rainfall": 68, "soilQuality": 75, "irrigation": 70}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"}),
        ("Moderately Suitable", 52, {"temperature": 42, "rainfall": 45, "soilQuality": 65, "irrigation": 42}, {"degradation": "Medium", "waterStress": "High", "foodSecurity": "High"}),
    ],
]

# Time period and scenario order for each region's 4 rows: (time_period, scenario_key) -> scenario_id resolved later
PREDICTION_ORDER = [
    ("current", "low"),
    ("current", "high"),
    ("future", "low"),
    ("future", "high"),
]


def _backfill_predictions(db: Session) -> None:
    """Add missing predictions for Sub-Saharan Africa current period (legacy 2-region DB)."""
    region2 = db.query(Region).filter(Region.name == "Sub-Saharan Africa").first()
    if not region2:
        return
    low = db.query(Scenario).filter(Scenario.name.like("%RCP 2.6%")).first()
    high = db.query(Scenario).filter(Scenario.name.like("%RCP 8.5%")).first()
    if not low or not high:
        return
    added = 0
    for scenario, sid in [(low, low.id), (high, high.id)]:
        if not db.query(SuitabilityPrediction).filter(
            and_(
                SuitabilityPrediction.region_id == region2.id,
                SuitabilityPrediction.scenario_id == sid,
                SuitabilityPrediction.time_period == "current",
            )
        ).first():
            score = 58 if sid == low.id else 48
            db.add(SuitabilityPrediction(
                region_id=region2.id,
                scenario_id=sid,
                time_period="current",
                suitability_class="Moderately Suitable",
                suitability_score=score,
                factors={"temperature": 55, "rainfall": 50, "soilQuality": 62, "irrigation": 55} if sid == low.id else {"temperature": 45, "rainfall": 40, "soilQuality": 55, "irrigation": 35},
                risks={"degradation": "Medium", "waterStress": "Medium", "foodSecurity": "Medium"} if sid == low.id else {"degradation": "Medium", "waterStress": "High", "foodSecurity": "Medium"},
            ))
            added += 1
    if added:
        db.commit()
        print(f"Backfilled {added} missing prediction(s) for Sub-Saharan Africa (current period).")


def _backfill_regions_and_predictions(db: Session) -> None:
    """If DB has fewer than 10 regions, add the extra regions and all 40 predictions."""
    region_count = db.query(Region).count()
    if region_count >= 10:
        return
    low = db.query(Scenario).filter(Scenario.name.like("%RCP 2.6%")).first()
    high = db.query(Scenario).filter(Scenario.name.like("%RCP 8.5%")).first()
    if not low or not high:
        return
    scenario_by_key = {"low": low, "high": high}
    added_regions = []
    for name, desc, lat, lng in EXTRA_REGIONS:
        if db.query(Region).filter(Region.name == name).first():
            continue
        r = Region(name=name, description=desc, coordinates={"lat": lat, "lng": lng})
        db.add(r)
        added_regions.append(r)
    if added_regions:
        db.commit()
        for r in added_regions:
            db.refresh(r)
    # Region IDs: 1=Central Eurasia, 2=Sub-Saharan Africa, 3..10 = extra in order
    all_regions = db.query(Region).order_by(Region.id).all()
    if len(all_regions) < 10:
        return
    # Predictions for region index 2..9 (0-based) are for regions 3..10; regions 1 and 2 already have predictions
    for idx, region in enumerate(all_regions):
        if idx >= len(REGION_PREDICTIONS):
            break
        preds = REGION_PREDICTIONS[idx]
        for i, (t_period, s_key) in enumerate(PREDICTION_ORDER):
            if i >= len(preds):
                break
            sc = scenario_by_key[s_key]
            if db.query(SuitabilityPrediction).filter(
                and_(
                    SuitabilityPrediction.region_id == region.id,
                    SuitabilityPrediction.scenario_id == sc.id,
                    SuitabilityPrediction.time_period == t_period,
                )
            ).first():
                continue
            cls, score, factors, risks = preds[i]
            db.add(SuitabilityPrediction(
                region_id=region.id,
                scenario_id=sc.id,
                time_period=t_period,
                suitability_class=cls,
                suitability_score=score,
                factors=factors,
                risks=risks,
            ))
    db.commit()
    if added_regions:
        print(f"Backfilled {len(added_regions)} new regions and predictions (10 regions total).")


def seed(db: Session) -> None:
    if db.query(Region).first() is not None:
        _backfill_predictions(db)
        _backfill_regions_and_predictions(db)
        return

    print("Seeding database...")

    regions_data = [
        ("Central Eurasia", "A vast region comprising diverse climates and agricultural zones.", 48.0, 66.0),
        ("Sub-Saharan Africa", "Region facing significant climate challenges and varying rainfall.", -1.0, 20.0),
    ] + EXTRA_REGIONS

    regions_list = []
    for name, desc, lat, lng in regions_data:
        r = Region(name=name, description=desc, coordinates={"lat": lat, "lng": lng})
        db.add(r)
        regions_list.append(r)
    db.commit()
    for r in regions_list:
        db.refresh(r)

    low = Scenario(
        name="Low Emission (RCP 2.6)",
        description="Stringent mitigation scenario.",
        co2_level=421,
    )
    high = Scenario(
        name="High Emission (RCP 8.5)",
        description="Baseline scenario with no additional efforts to constrain emissions.",
        co2_level=936,
    )
    db.add(low)
    db.add(high)
    db.commit()
    db.refresh(low)
    db.refresh(high)

    scenario_by_key = {"low": low, "high": high}
    for idx, region in enumerate(regions_list):
        if idx >= len(REGION_PREDICTIONS):
            break
        preds = REGION_PREDICTIONS[idx]
        for i, (t_period, s_key) in enumerate(PREDICTION_ORDER):
            if i >= len(preds):
                break
            cls, score, factors, risks = preds[i]
            sc = scenario_by_key[s_key]
            db.add(SuitabilityPrediction(
                region_id=region.id,
                scenario_id=sc.id,
                time_period=t_period,
                suitability_class=cls,
                suitability_score=score,
                factors=factors,
                risks=risks,
            ))
    db.commit()
    print("Database seeded successfully (10 regions, 40 predictions).")
