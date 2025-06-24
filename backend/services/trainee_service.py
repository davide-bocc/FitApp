from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from backend.db_models.workout import Workout, WorkoutAssignment


def get_assigned_workouts(db: Session, trainee_id: int) -> list[Workout]:

    return db.query(Workout) \
        .join(WorkoutAssignment) \
        .filter(WorkoutAssignment.trainee_id == trainee_id) \
        .all()


def get_workout_with_exercises(db: Session, workout_id: int, trainee_id: int) -> Workout:

    workout = db.query(Workout) \
        .join(WorkoutAssignment) \
        .options(joinedload(Workout.exercises)) \
        .filter(
        Workout.id == workout_id,
        WorkoutAssignment.trainee_id == trainee_id
    ) \
        .first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found or not assigned to you"
        )
    return workout


def update_workout_progress(
        db: Session,
        workout_id: int,
        trainee_id: int,
        is_completed: bool,
        exercise_id: Optional[int] = None
) -> None:

    if exercise_id is not None:
        pass
    else:
        assignment = db.query(WorkoutAssignment).filter(
            WorkoutAssignment.workout_id == workout_id,
            WorkoutAssignment.trainee_id == trainee_id
        ).first()

        if assignment:
            assignment.is_completed = is_completed
            assignment.completed_at = datetime.utcnow() if is_completed else None
            db.commit()