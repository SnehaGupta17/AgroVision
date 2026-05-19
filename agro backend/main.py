from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import User, UserRegister, FarmerInput
from agents import get_weather_intelligence, get_soil_intelligence

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, 
    allow_methods=["*"], allow_headers=["*"],
)

# --- AUTH ROUTES ---
@app.post("/register")
def register_user(user: UserRegister):
    with Session(engine) as session:
        if session.exec(select(User).where(User.username == user.username)).first():
            raise HTTPException(status_code=400, detail="Username taken")
        session.add(User(username=user.username, password=user.password))
        session.commit()
        return {"message": "User registered successfully!"}

@app.post("/login")
def login_user(user: UserRegister):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user.username)).first()
        if not db_user or db_user.password != user.password:
             raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"message": "Login successful", "user_id": db_user.id}

# --- YOUR ORCHESTRATION BRAIN ---
@app.post("/advise")
def get_recommendation(data: FarmerInput):
    
    # 1. Fetch live weather using the Village name
    weather = get_weather_intelligence(data.village)
    if "error" in weather:
        raise HTTPException(status_code=400, detail="Village not found in Maharashtra.")

    # 2. Feed BOTH Farmer Data + Live Weather Data into the ML Model
    soil = get_soil_intelligence(
        n=data.N, p=data.P, k=data.K, ph=data.ph,
        temp=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"]
    )
    
    if "error" in soil:
        raise HTTPException(status_code=500, detail="ML Model failed to generate prediction.")

    # 3. Member 4's Synthesis Logic
    top_crop = soil["top_crops"][0]
    final_advice = f"Based on live weather in {data.village} and your soil health, we highly recommend planting {top_crop.capitalize()}."
    
    if weather["weather_risk"] == "High":
        final_advice += " CAUTION: Extreme weather conditions detected. Delay sowing if possible."

    # 4. Return the massive, combined JSON payload for Member 1 (Frontend)
    return {
        "final_recommendation": final_advice,
        "top_3_crops": soil["top_crops"],
        "sustainability_score": soil["sustainability_score"],
        "fertilizer_advice": soil["fertilizer_status"],
        "live_weather": weather
    }