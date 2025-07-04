from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    user_id: int | None = None

class UserInToken(BaseModel):
    id: int
    email: str
    role: str

class LoginResponse(Token):
    user: UserInToken