from app.services.geospatial_service import read_geospatial_file


def test_read_shapefile_zip():
    gdf = read_geospatial_file(
        "sample_data/test_shapefile.zip"
    )

    assert len(gdf) == 2
    assert gdf.geometry.geom_type.tolist() == [
        "Point",
        "Point"
    ]
    assert str(gdf.crs) == "EPSG:4326"