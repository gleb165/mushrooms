from pydantic import BaseModel, EmailStr
from beanie import Document


class User(Document):
    email: EmailStr
    password: str
    role: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!",
            }
        }

    class Settings:
        name = "users"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None





