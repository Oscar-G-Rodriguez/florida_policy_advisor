# DATA_PROVENANCE_TABLE

This table is derived from `app/services/forecast.py` (metrics) and `app/data/registry.py` + `data/registry_state.json` (dataset metadata + retrieval dates).

Source org column is inferred from the dataset name prefix in `app/data/registry.py` (no separate field is stored).

Refresh script: `scripts/refresh_data.ps1` invokes `app/data/refresh.py`, which currently calls loaders for BLS, ACS, and FRED only.

| dataset_id | metric_id | human name | source org | URL | retrieval_date field/source | refresh method/script | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bls_unemployment | labor_unemployment_bls | Unemployment rate (BLS) | BLS | https://api.bls.gov/publicAPI/v2/timeseries/data/ | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| fred_macro | labor_unemployment_fred | Unemployment rate (FRED) | FRED | https://api.stlouisfed.org/fred/ | 2026-01-15 | HTTP API | license: FRED Terms of Use; loader implemented |
| fred_macro | fiscal_real_gdp | Real GDP | FRED | https://api.stlouisfed.org/fred/ | 2026-01-15 | HTTP API | license: FRED Terms of Use; loader implemented |
| census_acs_fl_county | housing_median_rent | Median gross rent | Census | https://api.census.gov/data.html | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| census_acs_fl_county | housing_rent_burden | Rent-to-income ratio | Census | https://api.census.gov/data.html | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| census_acs_fl_county | housing_vacancy_rate | Housing vacancy rate | Census | https://api.census.gov/data.html | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| census_acs_fl_county | housing_home_value | Median home value | Census | https://api.census.gov/data.html | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| census_acs_fl_county | general_population | Population | Census | https://api.census.gov/data.html | 2026-01-15 | HTTP API | license: Public domain; loader implemented |
| nces_ccd_grad | education_grad_rate | High school graduation rate | NCES | https://nces.ed.gov/ccd/ | unknown (registry_state.json missing entry) | Download | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| cdc_places | health_chronic_rate | Chronic disease prevalence | CDC | https://www.cdc.gov/places/ | unknown (registry_state.json missing entry) | Download | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| fema_nri | climate_risk_index | FEMA National Risk Index | FEMA | https://hazards.fema.gov/nri/ | unknown (registry_state.json missing entry) | Download | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| fhwa_hpms | infrastructure_road_condition | Road condition index | FHWA | https://highways.dot.gov/safety/data-analysis-tools/rsdp/rsdp-tools/highway-performance-monitoring-system-hpms | unknown (registry_state.json missing entry) | Download | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| epa_air | environment_pm25 | PM2.5 concentration | EPA | https://www.epa.gov/air-data | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| fbi_ucr | public_safety_violent_crime | Violent crime rate | FBI | https://cde.ucr.cjis.gov/ | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| eia_energy | energy_retail_price | Retail electricity price | EIA | https://www.eia.gov/opendata/ | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| fcc_bdc | broadband_access | Broadband availability | FCC | https://broadbandmap.fcc.gov/ | unknown (registry_state.json missing entry) | Download | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| census_popest | demographics_net_migration | Net migration | Census | https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| census_bds | business_startup_rate | Startup rate | Census | https://www.census.gov/programs-surveys/bds/data.API.html | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |
| usda_nass | agriculture_yield | Crop yield index | USDA | https://quickstats.nass.usda.gov/ | unknown (registry_state.json missing entry) | HTTP API | license: Public domain; NO LOADER IN REPO (expects drop-in CSV in data/processed or future loader) |