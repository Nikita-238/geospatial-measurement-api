from pathlib import Path


def test_polygon_measurement_api(client):
    file_path = Path(
        "sample_data/measurement_fixtures/polygon.zip"
    )

    with file_path.open("rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "polygon.zip",
                    file,
                    "application/zip"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["file_type"] == "zip"
    assert data["crs"] == "EPSG:4326"
    assert data["feature_count"] == 1
    assert data["status"] == "processed"

    file_id = data["id"]

    measurement_response = client.get(
        f"/api/files/{file_id}/measurements/"
    )

    assert measurement_response.status_code == 200

    measurements = measurement_response.json()

    assert len(measurements) == 1

    measurement = measurements[0]

    assert measurement["feature_id"] == 0
    assert measurement["geometry_type"] == "Polygon"
    assert measurement["area"] is not None
    assert measurement["area"] > 0
    assert measurement["length"] is None
    assert measurement["measurement_unit"] == "square_meters"
    assert measurement["status"] == "success"