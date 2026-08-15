from pydantic import BaseModel
from typing import List

class UserProfile(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    current_supplements: List[str] = []

class ChatRequest(BaseModel):
    user_message: str
    user_profile: UserProfile
    chat_history: List[dict] = []
    db_context: str = ""