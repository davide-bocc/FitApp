from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from backend.routers.enums import UserRole, ExerciseDifficulty, WorkoutStatus


# USER SCHEMAS
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.TRAINEE

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CoachOut(UserOut):
    trainees_count: Optional[int] = None

class TraineeOut(UserOut):
    completed_workouts: Optional[int] = None


# AUTH SCHEMAS
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class TokenResponse(Token):
    role: str
    user_id: int


# EXERCISE SCHEMAS
class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: ExerciseDifficulty
    target_muscles: str = Field(..., max_length=200)
    equipment_needed: Optional[str] = Field(None, max_length=200)

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: Optional[ExerciseDifficulty]
    target_muscles: Optional[str] = Field(None, max_length=200)

class ExerciseOut(ExerciseBase):
    id: int
    coach_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# WORKOUT SCHEMAS
class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: WorkoutStatus = WorkoutStatus.DRAFT

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(WorkoutBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[WorkoutStatus]

class WorkoutOut(WorkoutBase):
    id: int
    coach_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    exercises: List[ExerciseOut]

    model_config = ConfigDict(from_attributes=True)


# ASSIGNMENT SCHEMAS
class WorkoutAssignmentBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=500)

class WorkoutAssignmentCreate(WorkoutAssignmentBase):
    trainee_id: int

class WorkoutAssignmentUpdate(WorkoutAssignmentBase):
    is_completed: Optional[bool]

class WorkoutAssignmentOut(WorkoutAssignmentBase):
    id: int
    workout_id: int
    trainee_id: int
    assigned_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# PROGRESS SCHEMAS
class ExerciseProgressUpdate(BaseModel):
    is_completed: bool
    notes: Optional[str] = Field(None, max_length=500)

class WorkoutProgressUpdate(BaseModel):
    is_completed: bool
    exercise_id: Optional[int] = None

# Risoluzione dipendenze circolari
WorkoutOut.update_forward_refs()