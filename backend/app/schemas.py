from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class ScanCreate(BaseModel):
    urls: List[str]

class ScanOut(BaseModel):
    id: int
    urls: List[str]
    scan_results: Optional[Any]
    created_at: datetime

    class Config:
        orm_mode = True

class FindingCreate(BaseModel):
    title: str
    description: Optional[str]
    location: Optional[str]
    severity: Optional[str]
    ai_confidence: Optional[float]

class FindingOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    severity: Optional[str]
    ai_confidence: Optional[float]
    status: str
    poc_path: Optional[str]

    class Config:
        orm_mode = True

class ChatbotMessage(BaseModel):
    prompt: str
    context: Optional[Any] = None