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