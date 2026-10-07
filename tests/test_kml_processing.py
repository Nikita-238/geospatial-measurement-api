from app.services.geospatial_service import read_geospatial_file


def test_read_kml_file():
    gdf = read_geospatial_file("uploads/test.kml")

    assert len(gdf) == 1
    assert gdf.geometry.iloc[0].geom_type == "Point"