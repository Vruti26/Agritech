import requests

from services.sentinelhub_service import get_access_token


CATALOG_URL = "https://sh.dataspace.copernicus.eu/catalog/v1/search"

# Bounding box: [minimum longitude, minimum latitude,
#               maximum longitude, maximum latitude]
FIELD_BBOX = [72.50, 23.00, 72.51, 23.01]


def main():
    token = get_access_token()

    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": FIELD_BBOX,
        "datetime": "2026-10-01T00:00:00Z/2026-11-01T00:00:00Z",
        "limit": 20,
    }

    response = requests.post(
        CATALOG_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json",
            "Accept": "application/geo+json",
        },
        timeout=60,
    )

    response.raise_for_status()
    result = response.json()

    features = result.get("features", [])

    print(f"\nSentinel-2 L2A scenes found: {len(features)}")

    for feature in features:
        properties = feature.get("properties", {})

        print({
            "id": feature.get("id"),
            "datetime": properties.get("datetime"),
            "cloud_cover_percent": properties.get("eo:cloud_cover"),
        })

    context = result.get("context", {})
    if context.get("next") is not None:
        print("\nMore results may be available; catalogue pagination is needed.")


if __name__ == "__main__":
    main()