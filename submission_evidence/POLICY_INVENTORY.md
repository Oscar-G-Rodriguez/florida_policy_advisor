# POLICY_INVENTORY

Total policies: 20

## Sectors covered
agriculture, broadband, business_dynamism, climate, demographics, education, energy, environment, fiscal, general, health, housing, infrastructure, labor_market, public_safety

## Policies
- `rapid_employer_outreach` ? Rapid employer outreach and placement support (sectors: labor_market)
- `skills_apprenticeship` ? Sector-based upskilling and apprenticeships (sectors: labor_market, education)
- `childcare_transport_support` ? Childcare and transportation access (sectors: labor_market, housing)
- `affordable_housing_acceleration` ? Affordable housing pipeline acceleration (sectors: housing)
- `zoning_modernization` ? Zoning and permitting modernization (sectors: housing, infrastructure)
- `rental_assistance_preservation` ? Rental assistance and preservation (sectors: housing)
- `fiscal_reserve_strategy` ? Fiscal reserve and stabilization strategy (sectors: fiscal)
- `performance_budgeting` ? Performance budgeting and program reallocation (sectors: fiscal, general)
- `early_learning_support` ? Early learning and tutoring acceleration (sectors: education)
- `behavioral_health_access` ? Behavioral health access expansion (sectors: health, labor_market)
- `chronic_prevention` ? Chronic disease prevention investment (sectors: health)
- `flood_resilience` ? Flood resilience and mitigation program (sectors: climate, infrastructure)
- `transport_asset_management` ? Transportation asset management (sectors: infrastructure)
- `air_quality_enforcement` ? Targeted air quality enforcement (sectors: environment, health)
- `public_safety_violence_prevention` ? Violence prevention and community safety (sectors: public_safety)
- `grid_modernization` ? Grid modernization and energy efficiency (sectors: energy, climate)
- `broadband_last_mile` ? Last-mile broadband expansion (sectors: broadband, education, business_dynamism)
- `migration_attraction` ? Talent attraction and retention (sectors: demographics, labor_market)
- `small_business_capital` ? Small business capital access (sectors: business_dynamism, labor_market)
- `agriculture_resilience` ? Climate-smart agriculture and water efficiency (sectors: agriculture, climate)

## Effects schema
Each policy may include an `effects` object that maps `metric_id` -> numeric effect strength. The scoring engine multiplies each effect by the forecast pressure for that metric.