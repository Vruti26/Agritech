from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)  # Allow all origins

print("=" * 60)
print("🚀 EOSDA BACKEND - MOCK MODE (NO API KEYS NEEDED)")
print("=" * 60)
print("🌐 Backend: http://127.0.0.1:5000")
print("📁 Frontend: Open frontend/index.html in browser")
print("=" * 60)

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_ndvi_color(ndvi_value):
    """Convert NDVI value to color"""
    if ndvi_value > 0.7:
        return "#00ff00", "Excellent 🌿", "excellent"
    elif ndvi_value > 0.5:
        return "#aaff00", "Good ✅", "good"
    elif ndvi_value > 0.3:
        return "#ffff00", "Moderate ⚠️", "moderate"
    else:
        return "#ff0000", "Poor ❌", "poor"

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def home():
    """Home page"""
    return jsonify({
        "status": "success",
        "message": "✅ EOSDA Backend is running in MOCK MODE",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "mock_data",
        "note": "Using simulated data. Perfect for testing!",
        "endpoints": {
            "GET /": "This info page",
            "GET /test-satellite": "Test connection",
            "POST /analyze-field": "Analyze field (main function)",
            "GET /weather": "Get weather data",
            "GET /field-history": "Get field history",
            "GET /health": "Health check"
        }
    })

@app.route('/test-satellite', methods=['GET'])
def test_satellite():
    """Test endpoint - always returns success"""
    return jsonify({
        "status": "success",
        "message": "✅ Backend connected successfully!",
        "mode": "mock_mode",
        "note": "Using simulated satellite data - perfect for testing",
        "timestamp": datetime.now().isoformat(),
        "next_step": "Draw a field and click 'Analyze with Satellite'"
    })

@app.route('/analyze-field', methods=['POST', 'OPTIONS'])
def analyze_field():
    """Main analysis endpoint - returns mock data"""
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        
        if not data or 'bounds' not in data:
            return jsonify({
                "status": "error",
                "message": "No field bounds provided"
            }), 400
        
        field_name = data.get('name', f'Field_{random.randint(1000, 9999)}')
        bounds = data.get('bounds', [])
        
        print(f"🌾 Analyzing: {field_name}")
        print(f"📐 Bounds: {bounds[:2]}...")  # Print first 2 points only
        
        # Generate realistic mock NDVI data
        ndvi = round(random.uniform(0.25, 0.85), 2)
        
        # Get color and status
        ndvi_color, ndvi_status, ndvi_class = get_ndvi_color(ndvi)
        
        # Crop types for realism
        crop_types = ["Wheat", "Rice", "Corn", "Cotton", "Soybean", "Sugarcane"]
        selected_crop = random.choice(crop_types)
        
        # Generate recommendations based on NDVI
        if ndvi > 0.7:
            recommendations = [
                "Excellent crop health! Maintain current practices.",
                "Optimal growth conditions detected.",
                "Consider harvesting in 2-3 weeks.",
                "Monitor soil moisture for consistency."
            ]
        elif ndvi > 0.5:
            recommendations = [
                "Good vegetation health observed.",
                "Consider light fertilization in 10-14 days.",
                "Maintain current irrigation schedule.",
                "Check for early signs of pest activity."
            ]
        elif ndvi > 0.3:
            recommendations = [
                "Moderate stress detected in some areas.",
                "Increase irrigation frequency by 20%.",
                "Test soil for nutrient deficiencies.",
                "Consider adding organic compost."
            ]
        else:
            recommendations = [
                "⚠️ Immediate attention required!",
                "Severe vegetation stress detected.",
                "Increase irrigation immediately.",
                "Conduct comprehensive soil testing.",
                "Consult agricultural expert if condition persists."
            ]
        
        # Field statistics
        field_area = round(random.uniform(5, 50), 1)
        health_score = round(ndvi * 100, 1)
        
        # Build response
        response = {
            "status": "success",
            "data_type": "mock",
            "note": "Using simulated data. Real satellite data requires Sentinel Hub API keys.",
            "field_info": {
                "name": field_name,
                "area_acres": field_area,
                "crop_type": selected_crop,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "season": get_season()
            },
            "ndvi_analysis": {
                "value": ndvi,
                "color": ndvi_color,
                "status": ndvi_status,
                "class": ndvi_class,
                "interpretation": get_ndvi_interpretation(ndvi)
            },
            "statistics": {
                "mean_ndvi": ndvi,
                "min_ndvi": round(max(0.1, ndvi - 0.2), 2),
                "max_ndvi": round(min(1.0, ndvi + 0.15), 2),
                "health_score": health_score,
                "pixels_analyzed": random.randint(100000, 300000),
                "cloud_coverage": f"{random.randint(0, 20)}%",
                "resolution": "10m"
            },
            "recommendations": recommendations,
            "weather_impact": {
                "last_rainfall": f"{random.randint(0, 14)} days ago",
                "temperature": f"{random.randint(20, 35)}°C",
                "humidity": f"{random.randint(40, 85)}%",
                "condition": random.choice(["Sunny", "Partly Cloudy", "Clear"])
            },
            "next_steps": [
                f"Re-analyze in 7 days to track progress",
                "Compare with historical data",
                "Share report with farm manager"
            ]
        }
        
        print(f"✅ Analysis complete: NDVI={ndvi}, Status={ndvi_status}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error in analyze_field: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Analysis error: {str(e)}"
        }), 500

@app.route('/weather', methods=['GET'])
def weather():
    """Weather data endpoint"""
    lat = request.args.get('lat', '23.2599')
    lng = request.args.get('lng', '77.4126')
    
    return jsonify({
        "status": "success",
        "location": {"lat": lat, "lng": lng},
        "current": {
            "temperature": round(random.uniform(25, 35), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "precipitation": round(random.uniform(0, 5), 1),
            "wind_speed": round(random.uniform(5, 15), 1),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "condition": random.choice(["Sunny", "Partly Cloudy", "Clear", "Mostly Sunny"]),
            "pressure": round(random.uniform(1010, 1020), 1),
            "visibility": f"{random.randint(8, 15)} km"
        },
        "forecast": [
            {
                "day": "Today",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "high": random.randint(28, 34),
                "low": random.randint(20, 24),
                "condition": "Sunny",
                "rain_chance": f"{random.randint(0, 20)}%",
                "wind": f"{random.randint(5, 12)} km/h"
            },
            {
                "day": "Tomorrow",
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "high": random.randint(27, 33),
                "low": random.randint(19, 23),
                "condition": random.choice(["Partly Cloudy", "Clear"]),
                "rain_chance": f"{random.randint(10, 30)}%",
                "wind": f"{random.randint(8, 15)} km/h"
            },
            {
                "day": "Day 3",
                "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "high": random.randint(26, 32),
                "low": random.randint(18, 22),
                "condition": "Clear",
                "rain_chance": f"{random.randint(0, 10)}%",
                "wind": f"{random.randint(5, 10)} km/h"
            }
        ],
        "agricultural_advice": [
            "Good conditions for field work",
            "Ideal for irrigation activities",
            "Monitor soil moisture levels",
            "Favorable for fertilizer application"
        ]
    })

@app.route('/field-history', methods=['GET'])
def field_history():
    """Field history data"""
    field_id = request.args.get('field_id', '1')
    
    history = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(8):
        date = base_date + timedelta(days=i * 12)
        ndvi = 0.3 + random.random() * 0.5
        
        history.append({
            'date': date.strftime("%Y-%m-%d"),
            'ndvi': round(ndvi, 2),
            'rainfall_mm': round(random.random() * 20, 1),
            'temperature_avg': round(22 + random.random() * 10, 1),
            'health': 'Good' if ndvi > 0.5 else 'Moderate' if ndvi > 0.3 else 'Poor',
            'activity': random.choice(['Irrigation', 'Fertilization', 'Weeding', 'Monitoring', 'Harvest'])
        })
    
    # Sort by date
    history.sort(key=lambda x: x['date'])
    
    # Calculate trend
    if len(history) >= 2:
        trend = "improving" if history[-1]['ndvi'] > history[0]['ndvi'] else "stable"
    else:
        trend = "insufficient data"
    
    return jsonify({
        "status": "success",
        "field_id": field_id,
        "field_name": f"Agricultural Field #{field_id}",
        "total_entries": len(history),
        "history": history,
        "trend": trend,
        "average_ndvi": round(sum(h['ndvi'] for h in history) / len(history), 2),
        "season": get_season(),
        "note": "Simulated historical data for demonstration"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "eosda-backend-mock",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": "Active"
    })

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_ndvi_interpretation(ndvi):
    """Get human-readable interpretation of NDVI value"""
    if ndvi > 0.7:
        return "Very high vegetation density. Likely healthy, dense crops or forest."
    elif ndvi > 0.5:
        return "Moderate to high vegetation. Typical of healthy agricultural fields."
    elif ndvi > 0.3:
        return "Moderate vegetation. May indicate stress or sparse crop cover."
    elif ndvi > 0.1:
        return "Low vegetation. Could be bare soil, senescing crops, or urban areas."
    else:
        return "Very low or no vegetation. Possibly water, snow, or barren land."

def get_season():
    """Get current season based on month"""
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

# ============================================
# ERROR HANDLERS
# ============================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "GET /",
            "GET /test-satellite",
            "POST /analyze-field",
            "GET /weather",
            "GET /field-history",
            "GET /health"
        ]
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "detail": str(error) if app.debug else "Contact administrator"
    }), 500

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("📡 Server Configuration:")
    print(f"   Host: 127.0.0.1")
    print(f"   Port: 5000")
    print(f"   Mode: Development (Mock Data)")
    print("=" * 60)
    print("\n✅ Server ready! Open frontend in browser.")
    print("   Frontend URL: file:///path/to/frontend/index.html")
    print("=" * 60 + "\n")
    
    try:
        app.run(
            debug=True,
            port=5000,
            host='127.0.0.1',
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")