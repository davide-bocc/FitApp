from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db_models.base import Base
from backend.routers.enums import ExerciseDifficulty


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(Enum(ExerciseDifficulty), nullable=False)
    target_muscles = Column(String(200), nullable=False)
    coach_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relazioni
    coach = relationship("User", back_populates="coached_exercises")
    workouts = relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises"
    )

    def __repr__(self):
        return f"<Exercise(id={self.id}, name='{self.name}')>"