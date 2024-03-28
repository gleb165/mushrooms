from pydantic import BaseModel
from beanie import Document, PydanticObjectId


class Mushroom(Document):
    id_user: int
    name: str
    price: int
    predict: bool
    description: str
    image: bytes

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": 20,
                "name": "name!!!",
                "price": 20,
                "predict": True,
                "description": "description your mushroom",
                "image": "adad",
            }
        }

    class Settings:
        name = "Mushrooms"


class MushroomUpdate(BaseModel):
    id_user: int | None = None
    name: str | None = None
    price: int | None = None
    predict: bool | None = None
    description: str | None = None
    image: bytes

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": "id user which add mushroom",
                "name": "name!!!",
                "price": "1234!!!",
                "predict": "predict your mushroom",
                "description": "description your mushroom",
                "image": "adad"
            }
        }