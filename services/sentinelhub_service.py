import os
from services.ndvi_service import summarize_ndvi_response
from datetime import date
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely import transform

import requests
from dotenv import load_dotenv


# Load local environment variables during development.
load_dotenv()

# Official Copernicus Data Space OAuth token endpoint.
TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)


def get_access_token():
    """
    Obtain an OAuth access token for Sentinel Hub.
    """

    client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Sentinel Hub credentials are missing. "
            "Check your local .env configuration."
        )

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )
        response.raise_for_status()
        token_data = response.json()

    except requests.RequestException as exc:
        status = (
            exc.response.status_code
            if exc.response is not None
            else None
        )

        if exc.response is not None:
            print(
                "Copernicus authentication HTTP status:",
                status,
                flush=True,
            )
            print(
                "Copernicus authentication error:",
                exc.response.text[:1000],
                flush=True,
            )

        if status == 401:
            message = (
                "Copernicus authentication failed. "
                "Check your client credentials."
            )
        elif status == 403:
            message = (
                "Copernicus denied authentication. "
                "Check your account permissions."
            )
        elif status is not None:
            message = (
                f"Copernicus authentication request failed "
                f"(HTTP {status})."
            )
        else:
            message = "Could not contact the Copernicus authentication service."

        raise RuntimeError(message) from None

    except ValueError:
        raise RuntimeError(
            "Copernicus authentication returned invalid JSON."
        ) from None

    access_token = token_data.get("access_token")

    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError(
            "Copernicus did not return a valid access token."
        )

    return {
        "access_token": access_token,
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
    }

    """
    Obtain an OAuth access token for Sentinel Hub.

    Returns:
        A dictionary containing the access token and its expiry.

    Raises:
        RuntimeError: If configuration or authentication fails.
    """

    client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
    client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")

    # Check configuration before contacting the service.
    if not client_id or not client_secret:
        raise RuntimeError(
            "Sentinel Hub credentials are missing. "
            "Check your local .env configuration."
        )
     
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30,
        )

        response.raise_for_status()

  
    except requests.RequestException as exc:
      status = (
        exc.response.status_code
        if exc.response is not None
        else None
    )

    if exc.response is not None:
        print("Copernicus HTTP status:", status, flush=True)
        print(
            "Copernicus error response:",
            exc.response.text[:2000],
            flush=True,
        )
    else:
        print("Copernicus connection error:", str(exc), flush=True)

    if status == 400:
        message = (
            "Copernicus rejected the request. "
            "Check the API payload, geometry and evalscript."
        )
    elif status == 401:
        message = "Copernicus rejected the access token."
    elif status == 403:
        message = (
            "Access denied. Check Copernicus account permissions."
        )
    elif status == 429:
        message = "Copernicus rate limit reached. Try again later."
    elif status is not None:
        message = f"Satellite statistics request failed (HTTP {status})."
    else:
        message = "Could not contact the Copernicus statistics API."

    raise RuntimeError(message) from None


    access_token = token_data.get("access_token")

    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError(
            "Copernicus did not return a valid access token."
        )

    return {
        "access_token": access_token,
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
    }
NDVI_EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["B04", "B08", "SCL", "dataMask"]
        }],
        output: [
            {
                id: "ndvi",
                bands: 1,
                sampleType: "FLOAT32"
            },
            {
                id: "dataMask",
                bands: 1
            }
        ]
    };
}

function evaluatePixel(sample) {
    // Reject pixels without valid satellite data.
    if (sample.dataMask === 0) {
        return {
            ndvi: [0],
            dataMask: [0]
        };
    }

    // Reject cloud shadows, clouds, cirrus and snow.
    // Sentinel-2 Scene Classification Layer (SCL):
    // 3 = cloud shadow
    // 8 = medium-probability cloud
    // 9 = high-probability cloud
    // 10 = thin cirrus
    // 11 = snow or ice
    let rejectedClasses = [3, 8, 9, 10, 11];

    if (rejectedClasses.includes(sample.SCL)) {
        return {
            ndvi: [0],
            dataMask: [0]
        };
    }

    let red = sample.B04;
    let nir = sample.B08;
    let denominator = nir + red;

    if (denominator <= 0) {
        return {
            ndvi: [0],
            dataMask: [0]
        };
    }

    let ndvi = (nir - red) / denominator;

    return {
        ndvi: [ndvi],
        dataMask: [1]
    };
}
"""
DEBUG_NDVI_EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["B04", "B08", "dataMask"]
        }],
        output: [
            {
                id: "ndvi",
                bands: 1,
                sampleType: "FLOAT32"
            },
            {
                id: "dataMask",
                bands: 1
            }
        ]
    };
}

function evaluatePixel(sample) {
    if (sample.dataMask === 0) {
        return {
            ndvi: [0],
            dataMask: [0]
        };
    }

    let denominator = sample.B08 + sample.B04;

    if (denominator <= 0) {
        return {
            ndvi: [0],
            dataMask: [0]
        };
    }

    let ndvi = (sample.B08 - sample.B04) / denominator;

    return {
        ndvi: [ndvi],
        dataMask: [1]
    };
}
"""

def get_field_ndvi(geometry_geojson, start_date, end_date):
    """
    Request NDVI statistics for a field from Copernicus.

    Args:
        geometry_geojson: GeoJSON Polygon or Feature.
        start_date: Beginning of the observation period (YYYY-MM-DD).
        end_date: End of the observation period (YYYY-MM-DD).

    Returns:
        A dictionary containing the requested period and satellite statistics.
    """

    # 1. Validate the dates.
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except (TypeError, ValueError):
        raise ValueError("Dates must use YYYY-MM-DD format.") from None

    if start > end:
        raise ValueError("Start date must not be after end date.")

    if end > date.today():
        raise ValueError("End date cannot be in the future.")

    # 2. Extract the geometry from a GeoJSON Feature if necessary.
    if not isinstance(geometry_geojson, dict):
        raise ValueError("Field geometry must be a GeoJSON object.")

    if geometry_geojson.get("type") == "Feature":
        geometry_geojson = geometry_geojson.get("geometry")

    if not isinstance(geometry_geojson, dict):
        raise ValueError("Missing field geometry.")

    if geometry_geojson.get("type") != "Polygon":
        raise ValueError("Only Polygon geometry is supported.")

    try:
        polygon = shape(geometry_geojson)
    except (TypeError, ValueError, KeyError):
        raise ValueError("Invalid GeoJSON coordinates.") from None

    if polygon.is_empty or not polygon.is_valid:
        raise ValueError("Field polygon is empty or invalid.")

    min_lon, min_lat, max_lon, max_lat = polygon.bounds

    if not (
        -180 <= min_lon <= 180
        and -180 <= max_lon <= 180
        and -90 <= min_lat <= 90
        and -90 <= max_lat <= 90
    ):
        raise ValueError("Field coordinates are outside valid ranges.")

    # 3. Project the geographic polygon into a UTM coordinate system.
    # This allows us to request satellite sampling in metres.
    centroid = polygon.centroid

    utm_zone = min(
        max(int((centroid.x + 180) // 6) + 1, 1),
        60,
    )

    epsg_code = (
        32600 + utm_zone
        if centroid.y >= 0
        else 32700 + utm_zone
    )

    project = Transformer.from_crs(
        "EPSG:4326",
        f"EPSG:{epsg_code}",
        always_xy=True,
    ).transform

    projected_polygon = transform(
    polygon,
    project,
    interleaved=False,
)

    # 4. Calculate the field's geographic area.
    from pyproj import Geod

    geod = Geod(ellps="WGS84")
    signed_area, _ = geod.geometry_area_perimeter(polygon)
    area_hectares = abs(signed_area) / 10_000

    if area_hectares <= 0:
        raise ValueError("Field must have a positive area.")

    # 5. Obtain an OAuth token.
    token_data = get_access_token()
    access_token = token_data["access_token"]

    # 6. Construct the Statistical API request.
    payload = {
        "input": {
            "bounds": {
                "geometry": mapping(projected_polygon),
                "properties": {
                    "crs": (
                        "http://www.opengis.net/def/crs/EPSG/0/"
                        f"{epsg_code}"
                    )
                },
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "maxCloudCoverage": 80
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": f"{start.isoformat()}T00:00:00Z",
                "to": f"{end.isoformat()}T23:59:59Z",
            },
            "aggregationInterval": {
                "of": "P1D"
            },
            "lastIntervalBehavior": "SHORTEN",
            "evalscript": NDVI_EVALSCRIPT,
            "resx": 10,
            "resy": 10,
        },
    }

    # 7. Send the request to Copernicus.
    api_url = "https://sh.dataspace.copernicus.eu/statistics/v1"
    print("\nDEBUG: Statistics API endpoint:")
    print(api_url)

    # print("\nDEBUG: Request bounds:")
    # print(payload["input"]["bounds"])

    # print("\nDEBUG: Request time range:")
    # print(payload["aggregation"]["timeRange"])

    # print("\nDEBUG: Data collection:")
    # print(payload["input"]["data"])

    # print("\nDEBUG: Aggregation interval:")
    # print(payload["aggregation"]["aggregationInterval"])

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=90,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        status = (
            exc.response.status_code
            if exc.response is not None
            else None
        )       
        if exc.response is not None:
            error_text = exc.response.text

            if (
                status == 400
                and "larger than allowed 2500" in error_text
            ):
                raise RuntimeError(
                    "Your selected field is too large to analyse "
                    "in one request at 10-metre resolution. "
                    "Please draw a smaller field or divide it "
                    "into smaller sections, then try again. "
                    "Your resolution remains unchanged at 10 metres."
                ) from None

            print(
                "Copernicus Statistics error:",
                error_text[:2000],
                flush=True,
            )

        if status == 400:
            message = (
                "Copernicus rejected the request. "
                "Check the API payload, geometry and evalscript."
            )
        elif status == 401:
            message = "Copernicus rejected the access token."
        elif status == 403:
            message = (
                "Access denied. Check your Copernicus account "
                "permissions and service availability."
            )
        elif status == 429:
            message = "Copernicus rate limit reached. Try again later."
        elif status is not None:
            message = (
                f"Satellite statistics request failed "
                f"(HTTP {status})."
            )
        else:
            message = "Could not contact the Copernicus statistics API."

        raise RuntimeError(message) from None

    # 8. Parse the response.
    try:
        statistics = response.json()
    except ValueError:
        raise RuntimeError(
            "Copernicus returned an invalid JSON response."
        ) from None
    print("\nDEBUG: Raw Copernicus Statistics API response:")
    print(statistics)

    if not isinstance(statistics, dict):
        raise RuntimeError(
            "Copernicus returned an unexpected response structure."
        )
    print("\n--- NDVI STATISTICS DEBUG ---")
    print("Geometry pixel count:", statistics.get("geometryPixelCount"))

    for item in statistics.get("data", []):
     outputs = item.get("outputs", {})
    ndvi = outputs.get("ndvi", {})
    bands = ndvi.get("bands", {})
    band = bands.get("B0", {})
    stats = band.get("stats", {})

    print({
        "interval": item.get("interval"),
        "sampleCount": stats.get("sampleCount"),
        "noDataCount": stats.get("noDataCount"),
        "mean": stats.get("mean"),
    })

    print("--- END DEBUG ---\n")

    # 9. Return the response without inventing missing statistics.
    summary = summarize_ndvi_response(
    statistics=statistics,
    start_date=start.isoformat(),
    end_date=end.isoformat(),
    )

    
    return {
    "satellite": "Sentinel-2 L2A",
    "index": "NDVI",
    "field_area_hectares": round(area_hectares, 4),
    "start_date": start.isoformat(),
    "end_date": end.isoformat(),
    "requested_resolution_meters": 10,
    "ndvi_summary": summary,
}
