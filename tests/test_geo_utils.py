import pytest

from utils.geo_utils import analyse_field_geometry


VALID_FIELD = {
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


def test_valid_field_has_positive_area():
    result = analyse_field_geometry(VALID_FIELD)

    assert result["area_square_meters"] > 0
    assert result["area_hectares"] > 0
    assert result["area_acres"] > 0


def test_area_units_are_consistent():
    result = analyse_field_geometry(VALID_FIELD)

    assert result["area_hectares"] == pytest.approx(
        result["area_square_meters"] / 10_000,
        abs=0.0001,
    )


def test_rejects_non_polygon_geometry():
    invalid_field = {
        "type": "Point",
        "coordinates": [72.5000, 23.0000],
    }

    with pytest.raises(ValueError):
        analyse_field_geometry(invalid_field)


def test_rejects_out_of_range_coordinates():
    invalid_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [200, 23],
                [201, 23],
                [201, 24],
                [200, 24],
                [200, 23],
            ]
        ],
    }

    with pytest.raises(ValueError):
        analyse_field_geometry(invalid_field)


def test_rejects_self_intersecting_polygon():
    invalid_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [72.5000, 23.0000],
                [72.5020, 23.0020],
                [72.5020, 23.0000],
                [72.5000, 23.0020],
                [72.5000, 23.0000],
            ]
        ],
    }

    with pytest.raises(ValueError):
        analyse_field_geometry(invalid_field)