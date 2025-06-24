from __future__ import annotations
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from backend.routers.enums import WorkoutStatus

if TYPE_CHECKING:
    from .exercise_schemas import ExerciseOut
    from .user import UserOut


class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="Allenamento Forza")
    description: Optional[str] = Field(
        None,
        max_length=500,
        example="Scheda per aumentare la forza massimale"
    )
    status: WorkoutStatus = Field(default=WorkoutStatus.DRAFT)
    model_config = ConfigDict(from_attributes=True)


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[WorkoutStatus]
    exercises: Optional[List[int]] = Field(
        None,
        description="Lista di ID esercizi da associare al workout"
    )
    model_config = ConfigDict(from_attributes=True)


class WorkoutOut(WorkoutBase):
    id: int
    coach_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    exercises: List['ExerciseOut']


class WorkoutWithCoach(WorkoutOut):
    coach: 'UserOut'  # String literal


class WorkoutWithExercises(WorkoutWithCoach):
    exercises: List['ExerciseOut']
    total_duration: Optional[int] = Field(
        None,
        description="Durata totale stimata in minuti"
    )
    difficulty_level: Optional[str] = Field(
        None,
        description="Livello di difficoltà complessivo"
    )


class WorkoutAssignmentCreate(BaseModel):
    trainee_id: int = Field(..., description="ID dell'allievo")
    notes: Optional[str] = Field(
        None,
        max_length=500,
        example="Da completare entro venerdì"
    )
    model_config = ConfigDict(from_attributes=True)


class WorkoutProgressUpdate(BaseModel):
    workout_id: int = Field(..., description="ID del workout da aggiornare")
    trainee_id: int = Field(..., description="ID dell'allievo")
    completed: bool = Field(..., description="Stato di completamento")
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Note aggiuntive sul progresso"
    )
    date_completed: Optional[date] = Field(
        None,
        description="Data effettiva di completamento"
    )
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "workout_id": 1,
                "trainee_id": 123,
                "completed": True,
                "notes": "Esercizi completati con successo",
                "date_completed": "2023-12-01"
            }
        }
    )



def resolve_forward_refs():
    from .exercise_schemas import ExerciseOut
    from .user import UserOut

    WorkoutOut.model_rebuild(_types_namespace={
        'ExerciseOut': ExerciseOut,
        'UserOut': UserOut
    })
    WorkoutWithCoach.model_rebuild(_types_namespace={
        'ExerciseOut': ExerciseOut,
        'UserOut': UserOut
    })
    WorkoutWithExercises.model_rebuild(_types_namespace={
        'ExerciseOut': ExerciseOut,
        'UserOut': UserOut
    })


# Chiamata alla funzione di risoluzione
try:
    resolve_forward_refs()
except ImportError:
    pass