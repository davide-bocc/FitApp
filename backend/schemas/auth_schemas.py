from pydantic import BaseModel
from typing import Optional, Union
from backend.db_models.base import Base

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None