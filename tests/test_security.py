from pathlib import Path
from zipfile import ZipFile

import pytest

from app.services.geospatial_service import read_shapefile_zip


def test_reject_unsafe_zip_path(tmp_path):
    zip_path = tmp_path / "unsafe.zip"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "../../evil.shp",
            b"malicious content"
        )

    with pytest.raises(
        ValueError,
        match="unsafe file path"
    ):
        read_shapefile_zip(zip_path)


def test_reject_zip_without_shapefile(tmp_path):
    zip_path = tmp_path / "no_shapefile.zip"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "test.txt",
            b"not a shapefile"
        )

    with pytest.raises(
        ValueError,
        match="does not contain a Shapefile"
    ):
        read_shapefile_zip(zip_path)


def test_reject_multiple_shapefiles(tmp_path):
    zip_path = tmp_path / "multiple.zip"

    extract_dir = tmp_path / "multiple"
    extract_dir.mkdir()

    # Create fake .shp files so validation
    # reaches the multiple-Shapefile check.
    (extract_dir / "first.shp").write_bytes(b"")
    (extract_dir / "second.shp").write_bytes(b"")

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.write(
            extract_dir / "first.shp",
            "first.shp"
        )

        zip_file.write(
            extract_dir / "second.shp",
            "second.shp"
        )

    with pytest.raises(
        ValueError,
        match="multiple Shapefiles"
    ):
        read_shapefile_zip(zip_path)


def test_reject_missing_file():
    with pytest.raises(FileNotFoundError):
        read_shapefile_zip(
            Path("sample_data/does_not_exist.zip")
        )


def test_reject_corrupted_zip(tmp_path):
    zip_path = tmp_path / "corrupted.zip"

    zip_path.write_bytes(
        b"This is not a valid ZIP file."
    )

    with pytest.raises(
        ValueError,
        match="Invalid or corrupted ZIP file"
    ):
        read_shapefile_zip(zip_path)


def test_reject_invalid_shapefile(tmp_path):
    zip_path = tmp_path / "invalid_shapefile.zip"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr(
            "data.shp",
            b"This is not a valid Shapefile."
        )

    with pytest.raises(
        ValueError,
        match="Invalid or corrupted Shapefile"
    ):
        read_shapefile_zip(zip_path)