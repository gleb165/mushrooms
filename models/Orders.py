from pydantic import BaseModel
from beanie import Document, PydanticObjectId


class Order(Document):
    id_user: PydanticObjectId
    id_mushrooms: PydanticObjectId
    amount: int

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": "id user which add mushroom",
                "id_mushrooms": "id mushroom!!!",
                "amount": "1234!!!",
            }
        }

    class Settings:
        name = "orders"


class OrderUpdate(BaseModel):
    id_user: PydanticObjectId | None = None
    id_mushrooms: PydanticObjectId | None = None
    amount: int | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": "id user which add mushroom",
                "id_mushrooms": "id mushroom!!!",
                "amount": "1234!!!",
            }
        }