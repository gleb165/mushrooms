from fastapi import APIRouter, HTTPException, status
from models.Orders import Order, OrderUpdate
from beanie import PydanticObjectId
from database.connection import Database


Order_router = APIRouter(tags=["Order"])
Order_database = Database(Order)


@Order_router.get("/", response_model=list[Order])
async def retrieve_all_mushroom() -> list[Order]:
    return await Order_database.get_all()


@Order_router.get("/{id}", response_model=Order)
async def retrieve_one_mushroom(id: PydanticObjectId) -> Order:
    mushroom = await Order_database.get(id)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mushroom


@Order_router.post('/')
async def create_mushroom(body: Order) -> dict:
    await Order_database.save(body)
    return {'massage': 'your mushrooms correct create'}


@Order_router.put('/{id}', response_model=Order)
async def update_mushroom(body: OrderUpdate, id: PydanticObjectId) -> Order:
    update = await Order_database.update(id, body)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return update


@Order_router.delete('/{id}')
async def delete_mushroom(id: PydanticObjectId) -> dict:
    delete = await Order_database.delete(id)
    if delete:
        return {'massage': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="mushroom with supplied ID does not exist")