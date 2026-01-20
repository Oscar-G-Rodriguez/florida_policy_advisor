from app.data.loaders.bls import refresh as refresh_bls
from app.data.loaders.census_acs import refresh as refresh_acs
from app.data.loaders.fred import refresh as refresh_fred

LOADERS = [refresh_bls, refresh_acs, refresh_fred]
