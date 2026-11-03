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

result = get_field_ndvi(
    geometry_geojson=TEST_FIELD,
    start_date="2026-10-01",
    end_date="2026-10-31",
)

print("\nOctober NDVI summary:")
print(result["ndvi_summary"])