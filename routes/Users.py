from fastapi import APIRouter, HTTPException, status, Depends
from models.Users import User, Token
from beanie import PydanticObjectId
from database.connection import Database
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from passlib.context import CryptContext
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from datetime import timedelta
from auth.authenticate import get_current_user, get_current_active_user
from pydantic import EmailStr

hash_password = HashPassword()
user_router = APIRouter(tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


user_database = Database(User)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

hash_new = HashPassword()



class UserInDB(User):
    hashed_password: str




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


@user_router.delete('/{id}')
async def delete_mushroom(id: PydanticObjectId) -> dict:
    delete = await user_database.delete(id)
    if delete:
        return {'message': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User with supplied ID does not exist")


async def authenticate_user(User, email: EmailStr, password: str):
    user = await User.find_one(User.email == email)
    if not user:
        return False
    if not hash_password.verify_hash(password, user.password):
        return False
    return user


@user_router.post('/')
async def create_mushroom(body: User) -> dict:
    user_exist = await User.find_one(User.email == body.email)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided exists already."
        )
    hashed_password = hash_password.create_hash(body.password)
    body.password = hashed_password
    await user_database.save(body)
    return {
        "message": "User created successfully"
    }


@user_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(User, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@user_router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.email}]