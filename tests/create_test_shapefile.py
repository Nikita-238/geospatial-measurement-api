from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point


output_dir = Path("sample_data/test_shapefile")
output_dir.mkdir(
    parents=True,
    exist_ok=True
)

gdf = gpd.GeoDataFrame(
    {
        "name": ["Point A", "Point B"]
    },
    geometry=[
        Point(73.8780, 19.9975),
        Point(73.8800, 19.9990)
    ],
    crs="EPSG:4326"
)

gdf.to_file(
    output_dir / "test_shapefile.shp",
    driver="ESRI Shapefile"
)

print("Test Shapefile created successfully.")