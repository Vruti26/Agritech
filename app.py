from flask import Flask, request, jsonify
from services.sentinelhub_service import get_field_ndvi
from utils.geo_utils import analyse_field_geometry
from flask_cors import CORS

#  Flask application.
app = Flask(__name__)
CORS(app)

# Limit incoming JSON requests to 1 MB.
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


@app.get("/")
def home():
    """Return basic information about the application."""
    return jsonify({
        "application": "AgriTech",
        "version": "0.1.0",
        "message": "Agricultural intelligence API is running."
    }), 200


@app.get("/api/health")
def health_check():
    """Check whether the API is responding."""
    return jsonify({
        "status": "healthy"
    }), 200


@app.post("/api/fields/analyse")
def analyse_field():
    """Validate a field boundary and calculate its area."""

    # Read the incoming JSON request.
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Invalid or missing JSON request body."
        }), 400

    # Calculate the field area using our existing geospatial module.
    try:
        result = analyse_field_geometry(data)

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    # Return the calculated result to the client.
    return jsonify({
        "success": True,
        "field_analysis": result
    }), 200

@app.post("/api/fields/ndvi")
def analyse_field_ndvi():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid or missing JSON request body."
        }), 400

    geometry = data.get("geometry")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if geometry is None or start_date is None or end_date is None:
        return jsonify({
            "error": (
                "Required fields: geometry, start_date, end_date."
            )
        }), 400

    try:
        result = get_field_ndvi(
            geometry_geojson=geometry,
            start_date=start_date,
            end_date=end_date,
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    except RuntimeError as exc:
        return jsonify({
            "error": "Satellite analysis failed.",
            "details": str(exc),
        }), 502

    return jsonify({
        "success": True,
        "field_analysis": result,
    }), 200



@app.errorhandler(413)
def request_too_large(error):
    """Return a clear response for oversized requests."""
    return jsonify({
        "error": "Request body is too large."
    }), 413


if __name__ == "__main__":
    # Development server only; do not use this configuration in production.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )