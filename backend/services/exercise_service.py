from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.routers.enums import UserRole

try:
    from backend.db_models.exercise import Exercise
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from db_models.exercise import Exercise

if TYPE_CHECKING:
    from backend.schemas.exercise import ExerciseCreate, ExerciseUpdate


def create_exercise_for_coach(
        db: Session,
        coach_id: int,
        exercise_data: 'ExerciseCreate'
) -> Exercise:

    from backend.db_models.user_models import User
    coach = db.query(User).filter(
        User.id == coach_id,
        User.role == UserRole.COACH.value
    ).first()

    if not coach:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a coach or doesn't exist"
        )

    db_exercise = Exercise(
        **exercise_data.model_dump(),
        coach_id=coach_id
    )

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise


def get_exercises_for_user(
        db: Session,
        user_id: int,
        role: UserRole
) -> List[Exercise]:

    if role == UserRole.COACH:
        return db.query(Exercise).filter(Exercise.coach_id == user_id).all()
    else:
        return db.query(Exercise).filter(
            Exercise.is_public == True  # Esempio
        ).all()


def update_exercise_by_coach(
        db: Session,
        exercise_id: int,
        coach_id: int,
        exercise_data: 'ExerciseUpdate'
) -> Exercise:

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.coach_id == coach_id
    ).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found or you don't have permission"
        )

    update_data = exercise_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise_by_coach(
        db: Session,
        exercise_id: int,
        coach_id: int
) -> None:

    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.coach_id == coach_id
    ).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found or you don't have permission"
        )

    db.delete(exercise)
    db.commit()