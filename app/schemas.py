from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class Feed(BaseModel):
    topics: List[str]          
    vibe: str = "casual"       
    max_articles: Optional[int] = None 

class FeedCreate(Feed):
    pass

class FeedBase(Feed):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class User(BaseModel):  
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=72,
        description="Password must be between 8 and 72 characters")


class UserCreate(User):
    pass

class UserBase(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True