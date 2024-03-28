from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes.Users import user_router
from routes.Orders import Order_router
from routes.Mushrooms import mushrooms_router
from database.connection import Settings

from fastapi.middleware.cors import CORSMiddleware


origins = ["*"]

app = FastAPI()
s = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def init_db():
    await s.initialize_database()

# Register routes

app.include_router(user_router,  prefix="/user")
app.include_router(mushrooms_router, prefix="/order")
app.include_router(Order_router, prefix="/mushroom")



@app.get("/")
async def home():
    return RedirectResponse(url="/mushroom/")