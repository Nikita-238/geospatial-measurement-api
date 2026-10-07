from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

import geopandas as gpd
from pyproj import CRS


def read_geospatial_file(
    file_path: str | Path
) -> gpd.GeoDataFrame:
    """
    Read a supported geospatial file and return
    its features as a GeoDataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Geospatial file not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".kml":
        try:
            return gpd.read_file(
                file_path,
                driver="KML"
            )
        except Exception as error:
            raise ValueError(
                "Invalid or corrupted KML file."
            ) from error

    if extension == ".zip":
        return read_shapefile_zip(file_path)

    raise ValueError(
        f"Unsupported geospatial file format: {extension}"
    )


def read_shapefile_zip(
    file_path: Path
) -> gpd.GeoDataFrame:
    """
    Safely extract and read a Shapefile ZIP archive.

    Temporary extraction is automatically removed
    after processing.
    """

    try:
        with TemporaryDirectory(
            prefix="geospatial_extract_"
        ) as temp_dir:

            extract_dir = Path(temp_dir)

            with ZipFile(file_path, "r") as zip_file:

                # Validate every ZIP member before extraction
                for member in zip_file.infolist():

                    member_path = (
                        extract_dir / member.filename
                    )

                    if not member_path.resolve().is_relative_to(
                        extract_dir.resolve()
                    ):
                        raise ValueError(
                            "ZIP file contains an unsafe file path."
                        )

                zip_file.extractall(extract_dir)

            shapefiles = list(
                extract_dir.rglob("*.shp")
            )

            if not shapefiles:
                raise ValueError(
                    "ZIP file does not contain a Shapefile."
                )

            if len(shapefiles) > 1:
                raise ValueError(
                    "ZIP file contains multiple Shapefiles. "
                    "Please provide one Shapefile per ZIP."
                )

            try:
                return gpd.read_file(shapefiles[0])
            except Exception as error:
                raise ValueError(
                    "Invalid or corrupted Shapefile."
                ) from error

    except BadZipFile as error:
        raise ValueError(
            "Invalid or corrupted ZIP file."
        ) from error


def extract_features(
    gdf: gpd.GeoDataFrame
) -> list[dict]:
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
                "crs": (
                    gdf.crs.to_string()
                    if gdf.crs
                    else None
                ),
                "properties": properties,
            }
        )

    return features


def get_projected_crs(
    gdf: gpd.GeoDataFrame
) -> CRS:
    """
    Determine a suitable projected CRS for
    accurate distance and area measurements.
    """

    if gdf.crs is None:
        raise ValueError(
            "CRS is missing. Cannot calculate accurate measurements."
        )

    crs = CRS.from_user_input(gdf.crs)

    if crs.is_projected:
        return crs

    if not crs.is_geographic:
        raise ValueError(
            "Unsupported CRS type for measurement."
        )

    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError(
            "Could not determine a suitable projected CRS."
        )

    return CRS.from_user_input(
        projected_crs
    )


def calculate_measurements(
    gdf: gpd.GeoDataFrame
) -> list[dict]:
    """
    Calculate area and length for geospatial
    features using a projected CRS.
    """

    projected_crs = get_projected_crs(gdf)

    projected_gdf = gdf.to_crs(
        projected_crs
    )

    measurements = []

    for index, geometry in projected_gdf.geometry.items():

        geometry_type = geometry.geom_type

        result = {
            "feature_id": index,
            "geometry_type": geometry_type,
            "area": None,
            "length": None,
            "measurement_unit": None,
            "status": "success",
        }

        if geometry_type in {
            "Polygon",
            "MultiPolygon"
        }:
            result["area"] = geometry.area
            result["measurement_unit"] = (
                "square_meters"
            )

        elif geometry_type in {
            "LineString",
            "MultiLineString"
        }:
            result["length"] = geometry.length
            result["measurement_unit"] = "meters"

        elif geometry_type == "Point":
            result["measurement_unit"] = None

        else:
            result["status"] = "unsupported"

        measurements.append(result)

    return measurements