from __future__ import annotations
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr



class UserRole(str, Enum):

    COACH = "coach"
    TRAINEE = "trainee"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):

    email: EmailStr = Field(
        ...,
        examples=["user@example.com"],
        description="User's email address"
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["Mario Rossi"],
        description="Full name of the user"
    )


class UserCreate(UserBase):

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass123!"],
        description="Must contain at least 8 characters"
    )
    role: UserRole = Field(
        default=UserRole.TRAINEE,
        description="User role (coach or trainee)"
    )


class UserOut(UserBase):

    id: int = Field(..., examples=[1], description="Unique user ID")
    role: UserRole
    is_active: bool = Field(
        default=True,
        description="Account status (active/inactive)"
    )
    created_at: datetime = Field(
        ...,
        description="Registration timestamp"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Mario Rossi",
                "role": "trainee",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00"
            }
        }
    )


class TokenResponse(BaseModel):

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    role: str = Field(..., description="User role")


class TraineeOut(UserBase):

    id: int = Field(..., description="Unique user ID")
    is_active: bool = Field(..., description="Account status")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "trainee@example.com",
                "full_name": "Mario Rossi",
                "is_active": True
            }
        }
    )
