from sqlmodel import SQLModel, Field
from pydantic import BaseModel

# --- DATABASE TABLES ---
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str

# --- API DATA VALIDATORS (The New Contract) ---
class FarmerInput(BaseModel):
    village: str
    N: float      # Nitrogen
    P: float      # Phosphorus
    K: float      # Potassium
    ph: float     # Soil pH

class UserRegister(BaseModel):
    username: str
    password: str