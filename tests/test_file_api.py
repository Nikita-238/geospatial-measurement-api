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