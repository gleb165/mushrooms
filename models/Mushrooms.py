from fastapi import UploadFile, File
from pydantic import BaseModel, constr
from beanie import Document, PydanticObjectId
import base64


class Mushroom(Document):
    creator: str
    name: str
    price: int
    predict: bool
    description: str
    image: str


    class Settings:
        name = "Mushrooms"


class MushroomUpdate(BaseModel):
    name: str | None = None
    price: int | None = None
    description: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "name!!!",
                "price": "1234!!!",
                "description": "description your mushroom",
            }
        }