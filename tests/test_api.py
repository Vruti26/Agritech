from app import app


def test_health_endpoint():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy"
    }


def test_field_analysis_endpoint():
    app.config["TESTING"] = True

    field = {
        "type": "Polygon",
        "coordinates": [
            [
                [72.5000, 23.0000],
                [72.5020, 23.0000],
                [72.5020, 23.0020],
                [72.5000, 23.0020],
                [72.5000, 23.0000],
            ]
        ],
    }

    with app.test_client() as client:
        response = client.post(
            "/api/fields/analyse",
            json=field,
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["field_analysis"]["area_square_meters"] > 0
    assert data["field_analysis"]["area_hectares"] > 0


def test_field_analysis_rejects_a_point():
    point = {
        "type": "Point",
        "coordinates": [72.5000, 23.0000],
    }

    with app.test_client() as client:
        response = client.post(
            "/api/fields/analyse",
            json=point,
        )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data


def test_field_analysis_rejects_missing_json():
    with app.test_client() as client:
        response = client.post(
            "/api/fields/analyse",
            data="not json",
            content_type="text/plain",
        )

    assert response.status_code == 400