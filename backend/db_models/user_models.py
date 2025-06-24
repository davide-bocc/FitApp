from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db_models.base import Base
from sqlalchemy import Index



class UserRole(str, Enum):
    COACH = "coach"
    TRAINEE = "trainee"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relazioni aggiornate
    created_workouts = relationship("Workout", back_populates="coach", foreign_keys="Workout.coach_id")
    coached_exercises = relationship("Exercise", back_populates="coach")
    workout_assignments = relationship("WorkoutAssignment", back_populates="user")
    workouts = relationship("Workout", back_populates="coach", overlaps="created_workouts")