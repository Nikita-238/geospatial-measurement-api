from app.services.geospatial_service import (
    read_geospatial_file,
    extract_features
)


def test_extract_features():
    gdf = read_geospatial_file(
        "sample_data/test_shapefile.zip"
    )

    features = extract_features(gdf)

    assert len(features) == 2

    assert features[0]["feature_id"] == 0
    assert features[0]["geometry_type"] == "Point"
    assert features[0]["crs"] == "EPSG:4326"

    assert features[0]["properties"]["name"] == "Point A"
    assert features[1]["properties"]["name"] == "Point B"