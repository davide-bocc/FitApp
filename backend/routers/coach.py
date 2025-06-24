from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


def get_current_active_user():
    from backend.core.auth_dependencies import get_current_active_user
    return get_current_active_user()

def get_db():
    from backend.core.database import get_async_db
    return get_async_db()

from backend.db_models.user_models import User, UserRole
from backend.schemas.workout_schemas import WorkoutCreate, WorkoutOut, WorkoutAssignmentCreate
from backend.schemas.user import TraineeOut
from backend.services.coach_service import (
    create_workout_for_coach,
    assign_workout_to_trainee,
    get_coach_trainees
)

router = APIRouter(
    prefix="/coaches",
    tags=["Coaches"],
)

@router.post("/workouts/", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo i coach possono creare schede")
    return await create_workout_for_coach(db=db, coach_id=current_user.id, workout_data=workout_data)

@router.post("/workouts/assign", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
async def assign_workout(
    assignment_data: WorkoutAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i coach possono assegnare schede"
        )

    return await assign_workout_to_trainee(
        db=db,
        coach_id=current_user.id,
        workout_id=assignment_data.workout_id,
        trainee_id=assignment_data.trainee_id
    )

@router.get("/trainees/", response_model=List[TraineeOut])
async def list_trainees(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i coach possono vedere gli allievi"
        )

    return await get_coach_trainees(db=db, coach_id=current_user.id)

@router.get("/dashboard")
async def coach_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.COACH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i coach possono accedere alla dashboard"
        )

    return {"message": "Dashboard del coach"}