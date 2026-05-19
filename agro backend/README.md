📡 AgroVision Backend API - Integration Guide
Base URL (Local Testing): http://127.0.0.1:8001
Content-Type: application/json

Here are the three endpoints you need to connect the React frontend to the orchestration engine.

1. Register a New Farmer
Creates a new user account in the database.

Endpoint: POST /register

Request Body you must send:

JSON
{
  "username": "farmer_name",
  "password": "secure_password"
}
Success Response (200 OK):

JSON
{
  "message": "User registered successfully!"
}
Error Response (400 Bad Request): If the username is already taken.

JSON
{
  "detail": "Username taken"
}
2. Login Farmer
Authenticates the user and returns their database ID.

Endpoint: POST /login

Request Body you must send:

JSON
{
  "username": "farmer_name",
  "password": "secure_password"
}
Success Response (200 OK): (Save this user_id in React state/localStorage if needed later)

JSON
{
  "message": "Login successful",
  "user_id": 1
}
Error Response (401 Unauthorized):

JSON
{
  "detail": "Invalid credentials"
}
3. Get Crop & Fertilizer Recommendation (The Core AI)
This is the main orchestration endpoint. It takes the farmer's soil inputs and village name, fetches live weather data for that village, and runs it all through the ML model to generate advice.

Endpoint: POST /advise

Request Body you must send:

JSON
{
  "village": "Pune",
  "N": 50.5,
  "P": 40.0,
  "K": 35.0,
  "ph": 6.5
}
Success Response (200 OK): (Use this massive JSON to build the dashboard UI)

JSON
{
  "final_recommendation": "Based on live weather in Pune and your soil health, we highly recommend planting Cotton. CAUTION: Extreme weather conditions detected. Delay sowing if possible.",
  "top_3_crops": [
    "cotton",
    "soybean",
    "wheat"
  ],
  "sustainability_score": 85.5,
  "fertilizer_advice": {
    "Nitrogen": "Optimal",
    "Phosphorus": "Optimal",
    "Potassium": "Optimal"
  },
  "live_weather": {
    "temperature": 34.5,
    "humidity": 15,
    "rainfall": 0,
    "weather_risk": "High"
  }
}
Error Responses: * 400 Bad Request: If the village cannot be found by the weather API.

500 Internal Server Error: If the ML model fails to process the data.