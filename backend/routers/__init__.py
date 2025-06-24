from .auth import router as auth
from .coach import router as coach
from .exercise_router import router as exercise_router
from .trainee import router as trainee
from .workout_router import router as workout_router

__all__ = ['auth', 'coach', 'exercise_router', 'trainee', 'workout_router']
