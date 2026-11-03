from pyproj import Geod
from shapely.geometry import shape
from shapely.validation import explain_validity


# WGS84 is a standard reference model for geographic coordinates.
GEOD = Geod(ellps="WGS84")


def analyse_field_geometry(feature):
    """
    Validate a GeoJSON Polygon and calculate its geographic area.

    Returns:
        A dictionary containing the area in square metres,
        hectares, and acres.

    Raises:
        ValueError: If the supplied field geometry is invalid.
    """

    # 1. Check that the input is a dictionary.
    if not isinstance(feature, dict):
        raise ValueError("Field must be a JSON object.")

    # 2. Accept either a GeoJSON Feature or a Polygon.
    if feature.get("type") == "Feature":
        geometry = feature.get("geometry")
    else:
        geometry = feature

    if not isinstance(geometry, dict):
        raise ValueError("Missing field geometry.")

    if geometry.get("type") != "Polygon":
        raise ValueError("Only Polygon geometry is supported.")

    # 3. Convert the GeoJSON into a Shapely geometry.
    try:
        polygon = shape(geometry)
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("Invalid GeoJSON coordinates.") from exc

    # 4. Reject empty or invalid polygons.
    if polygon.is_empty:
        raise ValueError("The field polygon cannot be empty.")

    if not polygon.is_valid:
        reason = explain_validity(polygon)
        raise ValueError(f"Invalid field polygon: {reason}")

    # 5. Reject coordinates outside geographic limits.
    min_lon, min_lat, max_lon, max_lat = polygon.bounds

    if not (
        -180 <= min_lon <= 180
        and -180 <= max_lon <= 180
        and -90 <= min_lat <= 90
        and -90 <= max_lat <= 90
    ):
        raise ValueError("Coordinates are outside valid geographic ranges.")

    # 6. Calculate area using the WGS84 ellipsoid.
    signed_area, perimeter = GEOD.geometry_area_perimeter(polygon)

    area_square_meters = abs(signed_area)

    if area_square_meters <= 0:
        raise ValueError("The field must have a positive area.")

    # 7. Convert square metres into familiar land-area units.
    area_hectares = area_square_meters / 10_000
    area_acres = area_square_meters / 4_046.8564224

    return {
        "area_square_meters": round(area_square_meters, 2),
        "area_hectares": round(area_hectares, 4),
        "area_acres": round(area_acres, 4),
        "perimeter_meters": round(perimeter, 2),
    }