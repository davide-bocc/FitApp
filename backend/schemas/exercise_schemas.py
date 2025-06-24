from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: str  # str temporaneamente
    target_muscles: str = Field(..., max_length=200)

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    difficulty: Optional[str]  # str temporaneamente
    target_muscles: Optional[str] = Field(None, max_length=200)

class ExerciseOut(ExerciseBase):
    id: int
    coach_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


from backend.routers.enums import ExerciseDifficulty


ExerciseBase.__annotations__['difficulty'] = ExerciseDifficulty
ExerciseUpdate.__annotations__['difficulty'] = ExerciseDifficulty
