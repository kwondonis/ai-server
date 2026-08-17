from typing import Any

from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    current_supplements: list[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    user_message: str
    user_profile: UserProfile
    chat_history: list[dict[str, Any]] = Field(default_factory=list)
    db_context: str = ""
