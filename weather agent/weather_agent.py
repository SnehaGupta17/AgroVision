# Climate Risk & Weather Agent
## Maharashtra

import requests
import pandas as pd

API_KEY = "97a227f1b6b34be26ac4b556d2d60e59"

def fetch_weather(lat, lon):

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "rainfall": data.get("rain", {}).get("1h", 0),
        "wind": data["wind"]["speed"]
    }


def heat_stress(temp):
    if temp > 35:
        return 1
    elif temp >= 30:
        return 0.5
    return 0


def drought_risk(rainfall):
    if rainfall < 2:
        return 1
    elif rainfall < 10:
        return 0.5
    return 0


def humidity_risk(humidity):
    if humidity > 85:
        return 1
    elif humidity > 70:
        return 0.5
    return 0


def weather_risk_score(weather):
    return round(
        0.4 * heat_stress(weather["temp"]) +
        0.4 * drought_risk(weather["rainfall"]) +
        0.2 * humidity_risk(weather["humidity"]),
        2
    )


crop_requirements = {
    "Cotton": (21, 40),
    "Wheat": (10, 25),
    "Soybean": (15, 35)
}

def crop_suitability(weather):
    temp = weather["temp"]
    suitability = {}

    for crop, (min_t, max_t) in crop_requirements.items():
        suitability[crop] = 0.8 if min_t <= temp <= max_t else 0.4

    return suitability


def generate_weather_alerts(weather):
    alerts = []
    temp = weather["temp"]
    rainfall = weather["rainfall"]

    if temp >= 38:
        alerts.append("Heatwave risk. Avoid sowing and irrigate adequately.")

    if temp <= 8:
        alerts.append("Cold stress risk. Protect crops from low temperature.")

    if rainfall >= 80:
        alerts.append("Heavy rainfall expected. Ensure proper drainage.")

    if rainfall <= 5:
        alerts.append("Low rainfall. Irrigation required.")

    if not alerts:
        alerts.append("Weather conditions are normal. No immediate risk.")

    return alerts


def get_coordinates(village):

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={village},Maharashtra,IN&limit=1&appid={API_KEY}"

    data = requests.get(url).json()

    if len(data) == 0:
        return None, None

    lat = data[0]["lat"]
    lon = data[0]["lon"]

    return lat, lon

def fetch_forecast(lat, lon):

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    data = requests.get(url).json()

    temps = []
    rainfall = []

    for entry in data["list"][:10]:   # next ~30 hours
        temps.append(entry["main"]["temp"])
        rainfall.append(entry.get("rain", {}).get("3h", 0))

    return {
        "avg_temp": sum(temps)/len(temps),
        "total_rainfall": sum(rainfall)
    }
    

def forecast_risk_score(forecast):

    temp_risk = heat_stress(forecast["avg_temp"])
    rain_risk = drought_risk(forecast["total_rainfall"])

    return round(0.6 * temp_risk + 0.4 * rain_risk, 2)

def risk_level(score):

    if score < 0.3:
        return "Low"

    elif score < 0.6:
        return "Moderate"

    else:
        return "High"

def farmer_advice(current_risk, future_risk):

    advice = []

    if current_risk == "High":
        advice.append("Current weather conditions may harm crops.")

    if future_risk == "High":
        advice.append("High risk expected in coming days. Plan irrigation and avoid sowing.")

    if current_risk == "Low" and future_risk == "Low":
        advice.append("Weather conditions are good for farming.")

    return advice

def climate_agent(lat=None, lon=None, village=None):

    # If GPS coordinates are given
    if lat is not None and lon is not None:
        pass

    # Otherwise use village name
    elif village is not None:
        lat, lon = get_coordinates(village)

        if lat is None:
            return {"error": "Village not found"}

    else:
        return {"error": "Location not provided"}

    weather = fetch_weather(lat, lon)
    forecast = fetch_forecast(lat, lon)

    current_score = weather_risk_score(weather)
    future_score = forecast_risk_score(forecast)

    current_level = risk_level(current_score)
    future_level = risk_level(future_score)

    advice = farmer_advice(current_level, future_level)

    return {
    "latitude": lat,
    "longitude": lon,
    "temperature": weather["temp"],
    "humidity": weather["humidity"],
    "rainfall": weather["rainfall"],

    "current_weather_risk": current_level,
    "future_weather_risk": future_level,

    "alerts": generate_weather_alerts(weather),
    "crop_suitability": crop_suitability(weather),
    "farmer_advice": advice
}

climate_agent(lat=18.5204, lon=73.8567)


climate_agent(village="Dighi")

"""
Recommended folder structure

agrovision/
│
├── agents
│   ├── weather_agent.py
│   ├── soil_agent.py
│   ├── advisor_agent.py
│   └── market_agent.py
│
├── system
│   └── agrovision_system.py
│
└── app.py
"""