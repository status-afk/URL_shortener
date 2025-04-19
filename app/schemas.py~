from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None

class URLOut(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime

    class Config:
        from_attributes = True