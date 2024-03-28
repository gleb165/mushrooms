from pydantic import BaseModel, EmailStr
from beanie import Document


class User(Document):
    email: EmailStr
    password: str
    role: int | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!",
            }
        }

    class Settings:
        name = "users"


class UserSignIn(BaseModel):
    email: EmailStr
    password: str






