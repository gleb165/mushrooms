from pydantic import BaseModel
from beanie import Document, PydanticObjectId


class Order(Document):
    creator: str | None = None
    id_mushrooms: PydanticObjectId
    amount: int

    class Config:
        json_schema_extra = {
            "example": {
                "id_mushrooms": 'PydanticObjectId',
                "amount": 10,
            }
        }

    class Settings:
        name = "orders"


class OrderUpdate(BaseModel):
    amount: int | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "amount": "1234!!!",
            }
        }