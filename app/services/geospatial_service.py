from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd


def read_geospatial_file(file_path: str | Path) -> gpd.GeoDataFrame:
    """
    Read a supported geospatial file and return its features
    as a GeoDataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Geospatial file not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".kml":
        return gpd.read_file(
            file_path,
            driver="KML"
        )

    if extension == ".zip":
        return read_shapefile_zip(file_path)

    raise ValueError(
        f"Unsupported geospatial file format: {extension}"
    )


def read_shapefile_zip(file_path: Path) -> gpd.GeoDataFrame:
    """
    Extract a Shapefile ZIP archive and read the contained .shp file.
    """

    extract_dir = file_path.parent / file_path.stem

    extract_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with ZipFile(file_path, "r") as zip_file:
        zip_file.extractall(extract_dir)

    shapefiles = list(extract_dir.rglob("*.shp"))

    if not shapefiles:
        raise ValueError(
            "ZIP file does not contain a Shapefile (.shp)."
        )

    if len(shapefiles) > 1:
        raise ValueError(
            "ZIP file contains multiple Shapefiles. "
            "Please provide one Shapefile per ZIP."
        )

    return gpd.read_file(shapefiles[0])

def extract_features(gdf: gpd.GeoDataFrame) -> list[dict]:
    """
    Extract feature information from a GeoDataFrame.
    """

    features = []

    for index, row in gdf.iterrows():
        geometry = row.geometry

        properties = row.drop(
            labels=["geometry"]
        ).to_dict()

        features.append(
            {
                "feature_id": index,
                "geometry_type": geometry.geom_type,
                "geometry": geometry.__geo_interface__,
                "crs": gdf.crs.to_string() if gdf.crs else None,
                "properties": properties,
            }
        )

    return features