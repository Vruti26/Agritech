
import pytest

from services.ndvi_service import summarize_ndvi_response


SAMPLE_RESPONSE = {
    "status": "OK",
    "geometryPixelCount": 11554,
    "data": [
        {
            "interval": {
                "from": "2026-09-01T00:00:00Z",
                "to": "2026-10-01T00:00:00Z",
            },
            "outputs": {
                "ndvi": {
                    "bands": {
                        "B0": {
                            "stats": {
                                "min": -0.03671953082084656,
                                "max": 0.7474036812782288,
                                "mean": 0.30027938511487345,
                                "stDev": 0.21287261029336949,
                                "sampleCount": 11752,
                                "noDataCount": 10202,
                            }
                        }
                    }
                }
            },
        }
    ],
}


def test_extracts_ndvi_statistics():
    result = summarize_ndvi_response(
        SAMPLE_RESPONSE,
        "2026-09-01",
        "2026-10-31",
    )

    assert result["status"] == "observations_available"
    assert result["observation_count"] == 1

    observation = result["observations"][0]

    assert observation["mean_ndvi"] == 0.3003
    assert observation["min_ndvi"] == -0.0367
    assert observation["max_ndvi"] == 0.7474
    assert observation["std_dev"] == 0.2129
    assert observation["sample_count"] == 11752


def test_handles_empty_observations():
    result = summarize_ndvi_response(
        {"status": "OK", "data": []},
        "2026-09-01",
        "2026-10-31",
    )

    assert result["observation_count"] == 0
    assert result["has_observations"] is False
    assert result["status"] == "no_observations"


def test_rejects_reversed_dates():
    with pytest.raises(ValueError):
        summarize_ndvi_response(
            SAMPLE_RESPONSE,
            "2026-10-31",
            "2026-09-01",
        )


def test_rejects_unsuccessful_response():
    with pytest.raises(ValueError):
        summarize_ndvi_response(
            {"status": "ERROR", "data": []},
            "2026-09-01",
            "2026-10-31",
        )


def test_handles_multiple_daily_observations():
    statistics = {
        "status": "OK",
        "data": [
            {
                "interval": {
                    "from": "2026-10-08T00:00:00Z",
                    "to": "2026-10-09T00:00:00Z",
                },
                "outputs": {
                    "ndvi": {
                        "bands": {
                            "B0": {
                                "stats": {
                                    "min": 0.10,
                                    "max": 0.50,
                                    "mean": 0.30,
                                    "stDev": 0.08,
                                    "sampleCount": 1000,
                                    "noDataCount": 10,
                                }
                            }
                        }
                    }
                },
            },
            {
                "interval": {
                    "from": "2026-10-18T00:00:00Z",
                    "to": "2026-10-19T00:00:00Z",
                },
                "outputs": {
                    "ndvi": {
                        "bands": {
                            "B0": {
                                "stats": {
                                    "min": 0.15,
                                    "max": 0.60,
                                    "mean": 0.35,
                                    "stDev": 0.09,
                                    "sampleCount": 1000,
                                    "noDataCount": 20,
                                }
                            }
                        }
                    }
                },
            },
        ],
    }

    result = summarize_ndvi_response(
        statistics,
        "2026-10-01",
        "2026-10-31",
    )

    assert result["status"] == "observations_available"
    assert result["observation_count"] == 2
    assert len(result["observations"]) == 2

    first = result["observations"][0]
    second = result["observations"][1]

    assert first["interval_start"] == "2026-10-08T00:00:00Z"
    assert first["mean_ndvi"] == 0.30
    assert second["interval_start"] == "2026-10-18T00:00:00Z"
    assert second["mean_ndvi"] == 0.35

def test_calculates_valid_pixel_coverage():
    statistics = {
        "status": "OK",
        "geometryPixelCount": 851,
        "data": [
            {
                "interval": {
                    "from": "2026-10-01T00:00:00Z",
                    "to": "2026-10-02T00:00:00Z",
                },
                "outputs": {
                    "ndvi": {
                        "bands": {
                            "B0": {
                                "stats": {
                                    "min": 0.1,
                                    "max": 0.8,
                                    "mean": 0.5,
                                    "stDev": 0.1,
                                    "sampleCount": 851,
                                    "noDataCount": 0,
                                }
                            }
                        }
                    }
                },
            }
        ],
    }

    result = summarize_ndvi_response(
        statistics,
        "2026-10-01",
        "2026-10-31",
    )

    observation = result["observations"][0]

    assert observation["valid_pixel_percentage"] == 100.0
    assert observation["total_sample_count"] == 851


def test_calculates_partial_pixel_coverage():
    statistics = {
        "status": "OK",
        "geometryPixelCount": 851,
        "data": [
            {
                "interval": {
                    "from": "2026-10-06T00:00:00Z",
                    "to": "2026-10-07T00:00:00Z",
                },
                "outputs": {
                    "ndvi": {
                        "bands": {
                            "B0": {
                                "stats": {
                                    "min": 0.2,
                                    "max": 0.8,
                                    "mean": 0.6,
                                    "stDev": 0.1,
                                    "sampleCount": 851,
                                    "noDataCount": 310,
                                }
                            }
                        }
                    }
                },
            }
        ],
    }

    result = summarize_ndvi_response(
        statistics,
        "2026-10-01",
        "2026-10-31",
    )

    observation = result["observations"][0]

    assert observation["valid_pixel_percentage"] == 63.57
    assert observation["total_sample_count"] == 851


def test_rejects_inconsistent_pixel_counts():
    statistics = {
        "status": "OK",
        "geometryPixelCount": 851,
        "data": [
            {
                "interval": {
                    "from": "2026-10-06T00:00:00Z",
                    "to": "2026-10-07T00:00:00Z",
                },
                "outputs": {
                    "ndvi": {
                        "bands": {
                            "B0": {
                                "stats": {
                                    "min": 0.2,
                                    "max": 0.8,
                                    "mean": 0.6,
                                    "stDev": 0.1,
                                    "sampleCount": 851,
                                    "noDataCount": 900,
                                }
                            }
                        }
                    }
                },
            }
        ],
    }

    result = summarize_ndvi_response(
        statistics,
        "2026-10-01",
        "2026-10-31",
    )

    observation = result["observations"][0]

    assert observation["valid_pixel_percentage"] is None
    assert "inconsistent_pixel_counts" in observation["quality_warnings"]
    assert observation["requires_review"] is True