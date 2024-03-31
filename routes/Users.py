from fastapi import APIRouter, HTTPException, status
from models.Users import User
from beanie import PydanticObjectId
from database.connection import Database


user_router = APIRouter(tags=["User"])

user_database = Database(User)


@user_router.get("/", response_model=list[User])
async def retrieve_all_mushroom() -> list[User]:
    return await user_database.get_all()


@user_router.get("/{id}", response_model=User)
async def retrieve_one_mushroom(id: PydanticObjectId) -> User:
    mushroom = await user_database.get(id)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with supplied ID does not exist"
        )
    return mushroom


@user_router.post('/')
async def create_mushroom(body: User) -> dict:
    await user_database.save(body)
    return {'message': 'your User correct create'}


@user_router.delete('/{id}')
async def delete_mushroom(id: PydanticObjectId) -> dict:
    delete = await user_database.delete(id)
    if delete:
        return {'message': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User with supplied ID does not exist")

