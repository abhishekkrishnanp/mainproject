from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import json


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    education_level: Optional[str] = None
    course_degree: Optional[str] = None
    college: Optional[str] = None
    current_skills: Optional[str] = None      # comma-separated
    interests: Optional[str] = None           # comma-separated
    preferred_work_env: Optional[str] = None
    location: Optional[str] = None
    career_preferences: Optional[str] = None  # comma-separated


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    education_level: Optional[str] = None
    course_degree: Optional[str] = None
    college: Optional[str] = None
    current_skills: Optional[str] = None
    interests: Optional[str] = None
    preferred_work_env: Optional[str] = None
    location: Optional[str] = None
    career_preferences: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    age: Optional[int] = None
    education_level: Optional[str] = None
    course_degree: Optional[str] = None
    college: Optional[str] = None
    current_skills: Optional[str] = None
    interests: Optional[str] = None
    preferred_work_env: Optional[str] = None
    location: Optional[str] = None
    career_preferences: Optional[str] = None
    parent_access_code: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    user_id: Optional[int] = None
