from pathlib import Path

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
        gdf = gpd.read_file(
            file_path,
            driver="KML"
        )

    else:
        raise ValueError(
            f"Unsupported geospatial file format: {extension}"
        )

    return gdf