import geopandas as gpd

from shapely.geometry import Polygon

from app.services.geospatial_service import calculate_measurements


def test_polygon_area_measurement():
    polygon = Polygon([
        (73.8780, 19.9975),
        (73.8790, 19.9975),
        (73.8790, 19.9985),
        (73.8780, 19.9985),
        (73.8780, 19.9975),
    ])

    gdf = gpd.GeoDataFrame(
        {
            "name": ["Test Polygon"]
        },
        geometry=[polygon],
        crs="EPSG:4326"
    )

    measurements = calculate_measurements(gdf)

    assert len(measurements) == 1

    result = measurements[0]

    assert result["geometry_type"] == "Polygon"
    assert result["area"] is not None
    assert result["area"] > 0
    assert result["measurement_unit"] == "square_meters"
    assert result["status"] == "success"