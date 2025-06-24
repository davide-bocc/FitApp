from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db_models.workout import Workout
from backend.db_models.exercise import Exercise
from backend.db_models.user_models import User as UserModel
from backend.core.auth_dependencies import get_current_coach


# Import per evitare circular imports
def get_db():
    from backend.core.database import get_db as db_session
    return db_session()


# Import dei modelli e schemi
from backend.db_models import models
from backend.schemas.schemas import WorkoutCreate, WorkoutOut

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
async def create_workout(
        workout_data: WorkoutCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_coach)
):
    # Verifica che l'utente sia un coach
    if current_user.role != "coach":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i coach possono creare workout"
        )

    # Crea il workout
    workout = Workout(
        name=workout_data.name,
        description=workout_data.description,
        status=workout_data.status,
        coach_id=current_user.id
    )

    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    # Associa gli esercizi
    if workout_data.exercises:
        exercises = await db.execute(
            select(Exercise).where(Exercise.id.in_(workout_data.exercises))
        )
        exercises = exercises.scalars().all()

        if len(exercises) != len(workout_data.exercises):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uno o più esercizi non trovati"
            )

        workout.exercises.extend(exercises)
        await db.commit()
        await db.refresh(workout)

    return workout


@router.get("/", response_model=List[WorkoutOut])
def list_workouts(
        db: Session = Depends(get_db)
) -> List[WorkoutOut]:
    workouts = db.query(models.Workout).all()
    return workouts
