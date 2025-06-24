from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import per evitare circular imports
def get_db():
    from backend.core.database import get_db as db_session
    return db_session()

def get_current_active_user():
    from backend.core.auth_dependencies import get_current_active_user
    return get_current_active_user()

# Import dei modelli e schemi
from backend.db_models.user_models import User, UserRole
from backend.schemas.exercise_schemas import ExerciseCreate, ExerciseOut, ExerciseUpdate
from backend.services.exercise_service import (
    create_exercise_for_coach,
    get_exercises_for_user,
    update_exercise_by_coach,
    delete_exercise_by_coach
)

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.post("/", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can create exercises"
        )
    return create_exercise_for_coach(db=db, exercise_data=exercise_data, coach_id=current_user.id)

@router.get("/", response_model=List[ExerciseOut])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Ottenere la lista degli esercizi disponibili.
    Per i coach: mostra tutti gli esercizi creati da loro.
    Per gli allievi: mostra gli esercizi assegnati nelle schede attive.
    """
    return get_exercises_for_user(db=db, user_id=current_user.id, role=current_user.role)

@router.put("/{exercise_id}", response_model=ExerciseOut)
def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can update exercises"
        )
    return update_exercise_by_coach(
        db=db,
        exercise_id=exercise_id,
        coach_id=current_user.id,
        exercise_data=exercise_data
    )

@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches can delete exercises"
        )
    delete_exercise_by_coach(
        db=db,
        exercise_id=exercise_id,
        coach_id=current_user.id
    )
    return None