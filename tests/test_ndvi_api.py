from services.sentinelhub_service import get_field_ndvi


TEST_FIELD = {
    "type": "Polygon",
    "coordinates": [[
        [72.50, 23.00],
        [72.51, 23.00],
        [72.51, 23.01],
        [72.50, 23.01],
        [72.50, 23.00],
    ]],
}


def test_real_satellite_ndvi_request():
    """
    Integration test using the real Copernicus satellite API.

    Requires valid credentials, internet access, and API availability.
    """

    result = get_field_ndvi(
        geometry_geojson=TEST_FIELD,
        start_date="2026-09-01",
        end_date="2026-10-31",
    )

    assert result["satellite"] == "Sentinel-2 L2A"
    assert result["index"] == "NDVI"
    assert result["field_area_hectares"] > 0
    assert result["start_date"] == "2026-09-01"
    assert result["end_date"] == "2026-10-31"
    assert result["requested_resolution_meters"] == 10

    summary = result["ndvi_summary"]

    assert summary["status"] in {
        "observations_available",
        "no_observations",
    }
    assert isinstance(summary["observations"], list)

    print("\nSatellite:", result["satellite"])
    print("Field area:", result["field_area_hectares"], "hectares")
    print("NDVI summary:", summary)