
from datetime import date
import math


def safe_number(value):
    """Return a finite float, or None if unavailable or invalid."""
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(number):
        return None

    return number


def summarize_ndvi_response(statistics, start_date, end_date):
    """
    Convert a Copernicus Statistical API response into an NDVI summary.

    Calculate valid field-pixel coverage using:
        valid pixels = sampleCount - noDataCount
        coverage = valid pixels / geometryPixelCount * 100

    This assumes the evalscript dataMask excludes pixels outside
    the field and pixels excluded by the user's quality masks.
    """

    if not isinstance(statistics, dict):
        raise ValueError("Statistics response must be a JSON object.")

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except (TypeError, ValueError):
        raise ValueError("Dates must use YYYY-MM-DD format.") from None

    if start > end:
        raise ValueError("Start date must not be after end date.")

    if statistics.get("status") != "OK":
        raise ValueError("Satellite statistics are not marked as successful.")

    intervals = statistics.get("data")

    if not isinstance(intervals, list):
        raise ValueError("Satellite response is missing interval data.")

    def safe_count(value):
        """Return a non-negative integer, or None if unavailable."""
        number = safe_number(value)

        if number is None or number < 0 or not number.is_integer():
            return None

        return int(number)

    geometry_pixel_count = safe_count(
        statistics.get("geometryPixelCount")
    )

    observations = []

    for item in intervals:
        if not isinstance(item, dict):
            continue

        interval = item.get("interval") or {}
        outputs = item.get("outputs") or {}
        ndvi_output = outputs.get("ndvi") or {}
        bands = ndvi_output.get("bands") or {}
        band = bands.get("B0") or {}
        stats = band.get("stats") or {}

        if not isinstance(stats, dict) or not stats:
            continue

        interval_start = interval.get("from")
        interval_end = interval.get("to")

        mean_ndvi = safe_number(stats.get("mean"))
        min_ndvi = safe_number(stats.get("min"))
        max_ndvi = safe_number(stats.get("max"))
        std_dev = safe_number(stats.get("stDev"))

        sample_count = safe_count(stats.get("sampleCount"))
        no_data_count = safe_count(stats.get("noDataCount"))

        valid_pixel_count = None
        valid_pixel_percentage = None

        # Calculate valid pixels only when both API counts are valid.
        if sample_count is not None and no_data_count is not None:
            if no_data_count <= sample_count:
                valid_pixel_count = sample_count - no_data_count

        # Calculate coverage against the actual field geometry.
        if (
            valid_pixel_count is not None
            and geometry_pixel_count is not None
            and geometry_pixel_count > 0
        ):
            if valid_pixel_count <= geometry_pixel_count:
                valid_pixel_percentage = round(
                    valid_pixel_count / geometry_pixel_count * 100,
                    2
                )

        quality_warnings = []

        if mean_ndvi is None:
            quality_warnings.append("mean_unavailable")
        elif mean_ndvi < 0:
            quality_warnings.append("negative_mean_ndvi")

        if sample_count is None:
            quality_warnings.append("sample_count_unavailable")

        if no_data_count is None:
            quality_warnings.append("no_data_count_unavailable")

        if geometry_pixel_count is None:
            quality_warnings.append("geometry_pixel_count_unavailable")
        elif geometry_pixel_count == 0:
            quality_warnings.append("zero_geometry_pixel_count")

        if (
            sample_count is not None
            and no_data_count is not None
            and no_data_count > sample_count
        ):
            quality_warnings.append("inconsistent_pixel_counts")

        if (
            valid_pixel_count is not None
            and geometry_pixel_count is not None
            and valid_pixel_count > geometry_pixel_count
        ):
            quality_warnings.append("inconsistent_pixel_counts")

        if valid_pixel_count == 0:
            quality_warnings.append("no_valid_samples")

        if min_ndvi is None or max_ndvi is None:
            quality_warnings.append("incomplete_range_statistics")

        if (
            min_ndvi is not None
            and max_ndvi is not None
            and min_ndvi > max_ndvi
        ):
            quality_warnings.append("inconsistent_range_statistics")

        observations.append({
            "interval_start": interval_start,
            "interval_end": interval_end,

            "mean_ndvi": (
                round(mean_ndvi, 4)
                if mean_ndvi is not None
                else None
            ),

            "min_ndvi": (
                round(min_ndvi, 4)
                if min_ndvi is not None
                else None
            ),

            "max_ndvi": (
                round(max_ndvi, 4)
                if max_ndvi is not None
                else None
            ),

            "std_dev": (
                round(std_dev, 4)
                if std_dev is not None
                else None
            ),

            "geometry_pixel_count": geometry_pixel_count,
            "sample_count": sample_count,
            "no_data_count": no_data_count,

            # Kept for compatibility with the earlier response format.
            "total_sample_count": sample_count,

            "valid_pixel_count": valid_pixel_count,
            "valid_pixel_percentage": valid_pixel_percentage,

            "quality_warnings": quality_warnings,
            "requires_review": bool(quality_warnings),
        })

    return {
        "requested_period": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        "geometry_pixel_count": geometry_pixel_count,
        "observation_count": len(observations),
        "observations": observations,
        "has_observations": bool(observations),
        "status": (
            "observations_available"
            if observations
            else "no_observations"
        ),
    }
