from pathlib import Path


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_invalid_file_upload(client):
    files = {
        "file": (
            "test.txt",
            b"this is not a supported file",
            "text/plain"
        )
    }

    response = client.post(
        "/api/files/",
        files=files
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only .kml and .zip files are allowed."
    )


def test_file_not_found(client):
    response = client.get(
        "/api/files/999999/"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "File not found."
    )


def test_measurements_file_not_found(client):
    response = client.get(
        "/api/files/999999/measurements/"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "File not found."
    )


def test_successful_kml_upload(client):
    with open(
        "sample_data/test.kml",
        "rb"
    ) as file:

        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test.kml",
                    file,
                    "application/vnd.google-earth.kml+xml"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.kml"
    assert data["file_type"] == "kml"
    assert data["crs"] == "EPSG:4326"
    assert data["feature_count"] == 1
    assert data["status"] == "processed"


def test_oversized_file_upload(client):
    oversized_content = b"x" * (
        10 * 1024 * 1024 + 1
    )

    response = client.post(
        "/api/files/",
        files={
            "file": (
                "large.kml",
                oversized_content,
                "application/vnd.google-earth.kml+xml"
            )
        }
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "File size exceeds the 10 MB limit."
    )


def test_corrupted_kml_upload(client):
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "corrupted.kml",
                b"This is not valid KML content.",
                "application/vnd.google-earth.kml+xml"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid or corrupted KML file."
    )


def test_uploaded_file_is_cleaned_after_processing(client):
    upload_dir = Path("uploads")

    files_before = set(upload_dir.iterdir())

    with open(
        "sample_data/test.kml",
        "rb"
    ) as file:

        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "cleanup_test.kml",
                    file,
                    "application/vnd.google-earth.kml+xml"
                )
            }
        )

    assert response.status_code == 200

    files_after = set(upload_dir.iterdir())

    assert files_after == files_before