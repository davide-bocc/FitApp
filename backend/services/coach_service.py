from typing import TYPE_CHECKING
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from backend.schemas.workout_schemas import WorkoutCreate
    from backend.db_models.workout import Workout



def create_workout_for_coach(
        db: Session,
        coach_id: int,
        workout_data: 'WorkoutCreate'
) -> 'Workout':
    # Verificare che l'utente sia un coach
    from backend.db_models.user_models import User
    coach = db.query(User).filter(
        User.id == coach_id,
        User.role == "coach"
    ).first()

    if not coach:
        raise ValueError("User is not a coach or doesn't exist")

    # Convertire lo schema Pydantic in dizionario
    workout_dict = workout_data.model_dump()
    workout_dict["coach_id"] = coach_id

    # Creare il modello SQLAlchemy
    db_workout = Workout(**workout_dict)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

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