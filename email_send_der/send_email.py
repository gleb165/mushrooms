import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, BaseModel
from dotenv import load_dotenv
from auth.hash_password import HashPassword
from models.Users import User
hash_password = HashPassword()


load_dotenv('.env')

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=os.getenv('MAIL_PORT'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class EmailSchema(BaseModel):
    email: list[EmailStr]


async def send_message_email(body: User):
    verification_link = f'http://127.0.0.1:8000/user/{body.email}/{body.password}'

    html = f"""
    <p>Thank you for registering with our service!</p>
    <p>Click the link below to verify your email address:</p>
    <a href="{verification_link}">Verify Email</a>
    """
    message = MessageSchema(
        subject=str(f'{body.dict().get("email")} thanks for using us'),
        recipients=[body.dict().get("email")],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"message": "email has been sent"}