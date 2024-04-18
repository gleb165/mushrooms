from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from models.Users import User
from models.Mushrooms import Mushroom
from models.Orders import Order, OrderUpdate
from beanie import PydanticObjectId
from database.connection import Database
from auth.authenticate import get_current_user, get_current_active_user


Order_router = APIRouter(tags=["Order"])
Order_database = Database(Order)


@Order_router.get("/", response_model=list[Order])
async def retrieve_all_order(current_user: Annotated[User, Depends(get_current_active_user)]) -> list[Order]:
    return await Order_database.get_all()

@Order_router.get("/order", response_model=list[Order])
async def retrieve_one_order(current_user: Annotated[User, Depends(get_current_user)]) -> list[Order]:
    ord = await Order.find({'creator': current_user.email}).to_list()
    if not ord:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return ord
@Order_router.get("/{id}", response_model=Order)
async def retrieve_one_order(id: PydanticObjectId, current_user: Annotated[User, Depends(get_current_active_user)]) -> Order:
    mushroom = await Order_database.get(id)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mushroom


@Order_router.post('/')
async def create_order(current_user: Annotated[User, Depends(get_current_user)], body: Order) -> dict:
    body.creator = current_user.email
    mush = await Mushroom.get(body.id_mushrooms)
    if not mush:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mush with supplied ID does not exist"
        )
    await Order_database.save(body)
    return {'message': 'your mushrooms correct create'}


@Order_router.put('/{id}', response_model=Order)
async def update_order(current_user: Annotated[User, Depends(get_current_user)], body: OrderUpdate, id: PydanticObjectId) -> Order:
    order = await Order_database.get(id)
    if order.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    update = await Order_database.update(id, body)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return update


@Order_router.delete('/{id}')
async def delete_order(current_user: Annotated[User, Depends(get_current_user)], id: PydanticObjectId) -> dict:
    order = await Order_database.get(id)
    if current_user.email != order.creator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    delete = await Order_database.delete(id)
    if delete:
        return {'message': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="mushroom with supplied ID does not exist")
@Order_router.delete('/admin/{id}')
async def delete_order(current_user_ad: Annotated[User, Depends(get_current_active_user)], id: PydanticObjectId):
    delete = await Order_database.delete(id)
    if delete:
        return {'message': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="mushroom with supplied ID does not exist")