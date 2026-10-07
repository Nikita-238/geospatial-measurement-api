from pathlib import Path
import shutil

import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon


BASE_DIR = Path("sample_data/measurement_fixtures")

if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)

BASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_shapefile(name, geometry):
    output_dir = BASE_DIR / name
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    gdf = gpd.GeoDataFrame(
        {
            "name": [name]
        },
        geometry=[geometry],
        crs="EPSG:4326"
    )

    gdf.to_file(
        output_dir / f"{name}.shp",
        driver="ESRI Shapefile"
    )

    shutil.make_archive(
        str(BASE_DIR / name),
        "zip",
        root_dir=output_dir
    )


create_shapefile(
    "polygon",
    Polygon([
        (73.8780, 19.9975),
        (73.8790, 19.9975),
        (73.8790, 19.9985),
        (73.8780, 19.9985),
        (73.8780, 19.9975)
    ])
)

create_shapefile(
    "line",
    LineString([
        (73.8780, 19.9975),
        (73.8790, 19.9985)
    ])
)

create_shapefile(
    "point",
    Point(73.8800, 19.9990)
)

print("Measurement Shapefile fixtures created successfully.")