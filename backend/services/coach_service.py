from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.workout_schemas import WorkoutCreate
from backend.db_models.workout import Workout
from backend.db_models.user_models import User, UserRole


async def create_workout_for_coach(
    db: AsyncSession,
    coach_id: int,
    workout_data: WorkoutCreate
) -> Workout:
    # Verificare che l'utente sia un coach
    result = await db.execute(select(User).where(User.id == coach_id))
    coach = result.scalars().first()

    if not coach or coach.role != "coach":
        raise HTTPException(status_code=404, detail="Coach not found")

    workout_dict = workout_data.model_dump()
    if 'status' in workout_dict and not hasattr(Workout, 'status'):
        del workout_dict['status']

    # Creare il workout
    db_workout = Workout(
        **workout_dict,
        coach_id=coach_id
    )

    db.add(db_workout)
    await db.commit()
    await db.refresh(db_workout)

    return db_workout

def assign_workout_to_trainee(db: Session, coach_id: int, workout_id: int, trainee_id: int):
    # Verifica che la scheda appartenga al coach
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.coach_id == coach_id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Scheda non trovata")

    # Verifica che l'utente sia un allievo
    trainee = db.query(User).filter(
        User.id == trainee_id,
        User.role == UserRole.TRAINEE
    ).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Allievo non valido")

    # Crea l'assegnazione
    assignment = WorkoutAssignment(
        workout_id=workout_id,
        trainee_id=trainee_id
    )
    db.add(assignment)
    db.commit()
    return workout

def get_coach_trainees(db: Session, coach_id: int):
    return db.query(User).filter(
        User.coach_id == coach_id,
        User.role == UserRole.TRAINEE
    ).all()