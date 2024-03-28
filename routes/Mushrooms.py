from fastapi import APIRouter, HTTPException, status
from models.Mushrooms import Mushroom, MushroomUpdate
from beanie import PydanticObjectId
from database.connection import Database


mushrooms_router = APIRouter(tags=["Mushroom"])
mushrooms_database = Database(Mushroom)


@mushrooms_router.get("/", response_model=list[Mushroom])
async def retrieve_all_mushroom() -> list[Mushroom]:
    return await mushrooms_database.get_all()


@mushrooms_router.get("/{id}", response_model=Mushroom)
async def retrieve_one_mushroom(id: PydanticObjectId) -> Mushroom:
    mushroom = await mushrooms_database.get(id)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mushroom


@mushrooms_router.post('/')
async def create_mushroom(body: Mushroom) -> dict:
    await mushrooms_database.save(body)
    return {'massage': 'your mushrooms correct create'}


@mushrooms_router.put('/{id}', response_model=Mushroom)
async def update_mushroom(body: MushroomUpdate, id: PydanticObjectId) -> Mushroom:
    update = await mushrooms_database.update(id, body)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return update


@mushrooms_router.delete('/{id}')
async def delete_mushroom(id: PydanticObjectId) -> dict:
    delete = await mushrooms_database.delete(id)
    if delete:
        return {'massage': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="mushroom with supplied ID does not exist")

