import geopandas as gpd
from shapely.geometry import Polygon

import pytest

from app.services.geospatial_service import calculate_measurements


def test_reject_missing_crs():
    gdf = gpd.GeoDataFrame(
        {
            "name": ["Test Area"]
        },
        geometry=[
            Polygon([
                (0, 0),
                (1, 0),
                (1, 1),
                (0, 1),
                (0, 0)
            ])
        ],
        crs=None
    )

    with pytest.raises(
        ValueError,
        match="CRS is missing"
    ):
        calculate_measurements(gdf)