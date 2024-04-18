from fastapi import APIRouter, HTTPException, status, Depends
from models.Users import User, Token, UserUpdate
from database.connection import Database
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from passlib.context import CryptContext
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from datetime import timedelta
from auth.authenticate import get_current_user, get_current_active_user
from email_send_der.send_email import send_message_email
from email_send_der.change_password import send_message_email_for_change_password
from beanie import PydanticObjectId

from pydantic import EmailStr

hash_password = HashPassword()
user_router = APIRouter(tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


user_database = Database(User)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30





class UserInDB(User):
    hashed_password: str




@user_router.get("/", response_model=list[User])
async def retrieve_all_mushroom(current_user: Annotated[User, Depends(get_current_active_user)]) -> list[User]:
    return await user_database.get_all()


@user_router.get("/{email}", response_model=User)
async def retrieve_one_user(email: EmailStr, current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    mushroom = await user_database.get_user(email)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with supplied ID does not exist"
        )
    return mushroom


@user_router.delete('/{email}')
async def delete_user(email: EmailStr, current_user: Annotated[User, Depends(get_current_active_user)]) -> dict:
    delete = await user_database.delete_user(email)
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
    if user.verified is None:
        return False
    return user

@user_router.get('/{email}/{password}')
async def verification_user(email: EmailStr, password: str) -> dict:
    user_old = await user_database.get_user(email)
    if not user_old:
        return {'message': 'not correct link'}
    if not user_old.password == password:
        return {'message': 'not correct password'}
    user_old.verified = True
    await user_database.update(user_old.id, user_old)

    return {'message': 'your account verified'}

@user_router.post('/')
async def create_user(body: User) -> dict:
    user_exist = await User.find_one(User.email == body.email)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided exists already."
        )
    hashed_password = hash_password.create_hash(body.password)
    body.password = hashed_password
    await send_message_email(body=body)
    await user_database.save(body)
    return {
        "message": "User created successfully"
    }
@user_router.patch('/add_admin_role')
async def admin(email: EmailStr, current_user: Annotated[User, Depends(get_current_active_user)]):
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided not exists."
        )
    user.role = True
    user_up = await user_database.update(user.id, user)
    if not user_up:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with supplied ID does not exist"
        )

@user_router.patch('/password/change')
async def change_password(body: User) -> dict:
    user_exist = await User.find_one(User.email == body.email)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided not exists."
        )
    body.id = user_exist.id
    await send_message_email_for_change_password(body)
    return {'message': 'please confirm your email before change your password'}


@user_router.get('/password/change/link/{email}/{password}')
async def change_password(email: EmailStr, password: str) -> dict:
    usr = await User.find_one(User.email == email)
    if not usr:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided no exists."
        )
    password = hash_password.create_hash(password)
    usr.password = password
    update = await user_database.update(usr.id, usr)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return {'message': 'your password be change'}


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
