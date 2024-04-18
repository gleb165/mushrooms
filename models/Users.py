from pydantic import BaseModel, EmailStr
from beanie import Document


class User(Document):
    email: EmailStr
    password: str
    role: bool | None = None
    verified: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!",
            }
        }

    class Settings:
        name = "users"


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None





