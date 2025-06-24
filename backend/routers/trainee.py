from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Import per evitare circular imports
def get_db():
    from backend.core.database import get_async_db
    return get_async_db()

def get_current_active_user():
    from backend.core.auth_dependencies import get_current_active_user
    return get_current_active_user()

# Import dei modelli e schemi
from backend.db_models.user_models import UserRole, User
from backend.schemas.workout_schemas import (
    WorkoutOut,
    WorkoutWithExercises,
    WorkoutProgressUpdate
)
from backend.services.trainee_service import (
    get_assigned_workouts,
    get_workout_with_exercises,
    update_workout_progress
)

router = APIRouter(prefix="/trainees", tags=["Trainees"])

@router.get("/workouts/", response_model=List[WorkoutOut])
async def get_my_workouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottenere tutte le schede di allenamento assegnate"""
    if current_user.role != UserRole.TRAINEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainees can access this endpoint"
        )
    return await get_assigned_workouts(db=db, trainee_id=current_user.id)

@router.get("/workouts/{workout_id}", response_model=WorkoutWithExercises)
async def get_workout_details(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottenere i dettagli di una specifica scheda"""
    if current_user.role != UserRole.TRAINEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainees can access this endpoint"
        )
    return await get_workout_with_exercises(
        db=db,
        workout_id=workout_id,
        trainee_id=current_user.id
    )

@router.patch("/workouts/{workout_id}/progress", response_model=WorkoutOut)
async def update_progress(
    workout_id: int,
    progress_data: WorkoutProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna lo stato di completamento"""
    if current_user.role != UserRole.TRAINEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli allievi possono aggiornare i progressi"
        )

    if workout_id != progress_data.workout_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workout ID in path doesn't match body data"
        )

    if current_user.id != progress_data.trainee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non puoi aggiornare i progressi di altri utenti"
        )

    return await update_workout_progress(
        db=db,
        workout_id=workout_id,
        trainee_id=current_user.id,
        progress_data=progress_data
    )