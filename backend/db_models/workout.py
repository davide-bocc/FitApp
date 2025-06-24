from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db_models.base import Base
from sqlalchemy import Index

# Tabella di associazione molti-a-molti
workout_exercises = Table(
    'workout_exercises',
    Base.metadata,
    Column('workout_id', Integer, ForeignKey('workouts.id'), primary_key=True),
    Column('exercise_id', Integer, ForeignKey('exercises.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

class Workout(Base):
    __tablename__ = "workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relazioni
    coach = relationship(
        "User",
        back_populates="created_workouts",
        foreign_keys=[coach_id]
    )

    exercises = relationship(
        "Exercise",
        secondary=workout_exercises,
        back_populates="workouts",
        lazy="selectin"
    )

    assignments = relationship(
        "WorkoutAssignment",
        back_populates="workout",
        cascade="all, delete",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Workout(id={self.id}, name='{self.name[:20]}...')>"


class WorkoutAssignment(Base):
    __tablename__ = 'workout_assignments'
    __table_args__ = (
        Index('ix_workout_assignments_user_workout', 'user_id', 'workout_id', unique=True),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey('workouts.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    workout = relationship("Workout", back_populates="assignments")
    user = relationship("User", back_populates="workout_assignments")