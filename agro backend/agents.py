import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 1. SOIL AGENT (Member 3) - ML Model Setup
# ==========================================
print("DEBUG: Training Soil ML Model (This might take a second)...")
try:
    # Load the CSV and train the model ONCE when the server starts
    data = pd.read_csv("Crop_recommendation.csv") # Check spelling if this fails!
    X = data[['N','P','K','temperature','humidity','ph','rainfall']]
    y = data['label']
    
    soil_model = RandomForestClassifier(n_estimators=200, random_state=42)
    soil_model.fit(X, y)
    print("DEBUG: ML Model trained successfully!")
except Exception as e:
    print(f"DEBUG: ERROR LOADING CSV! Make sure the file is in the folder. {e}")
    soil_model = None

def get_soil_intelligence(n, p, k, ph, temp, humidity, rainfall):
    if soil_model is None:
        return {"error": "ML Model is down"}
        
    # Sustainability Score Logic
    water_efficiency = 100 - abs(ph - 7) * 10
    nutrient_balance = (n + p + k) / 3
    soil_health = 100 - abs(ph - 6.5) * 10
    sus_score = round((0.4 * water_efficiency) + (0.3 * nutrient_balance) + (0.3 * soil_health), 2)
    
    # ML Prediction
    input_df = pd.DataFrame([{
        "N": n, "P": p, "K": k, 
        "temperature": temp, "humidity": humidity, 
        "ph": ph, "rainfall": rainfall
    }])
    
    probs = soil_model.predict_proba(input_df)[0]
    crops = soil_model.classes_
    
    # Get Top 3 Crops
    results = list(zip(crops, probs))
    results = sorted(results, key=lambda x: x[1], reverse=True)
    top_crops = [crop for crop, prob in results[:3]]
    
    return {
        "top_crops": top_crops,
        "sustainability_score": sus_score,
        "fertilizer_status": {
            "Nitrogen": "Low" if n < 40 else "Optimal",
            "Phosphorus": "Low" if p < 30 else "Optimal",
            "Potassium": "Low" if k < 30 else "Optimal"
        }
    }

# ==========================================
# 2. WEATHER AGENT (Member 2)
# ==========================================
API_KEY = "97a227f1b6b34be26ac4b556d2d60e59"

def get_weather_intelligence(village: str):
    # Get Coordinates
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={village},Maharashtra,IN&limit=1&appid={API_KEY}"
    geo_data = requests.get(url).json()
    
    if len(geo_data) == 0:
        return {"error": "Village not found"}
        
    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
    
    # Get Live Weather
    w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    w_data = requests.get(w_url).json()
    
    temp = w_data["main"]["temp"]
    humidity = w_data["main"]["humidity"]
    rainfall = w_data.get("rain", {}).get("1h", 0) # Fallback to 0 if no rain
    
    # Simplified Risk Scoring
    risk = "Low"
    if temp > 35 or rainfall > 80:
        risk = "High"
    elif temp > 30 or rainfall < 5:
        risk = "Moderate"
        
    return {
        "temperature": temp,
        "humidity": humidity,
        "rainfall": rainfall,
        "weather_risk": risk
    }