
### run venv\Scripts\activate.bat
### or  source e:/Misc/Paul/Programming/python/FastAPI/venv/Scripts/activate
### then
###     uvicorn app.main:app --reload --no-use-colors

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Using SQLAlchemy as an ORM to "hide" all SQL processing
from . import models
from .config import settings
from .database import engine
from .routers import posts, users, auth, votes

# Make sure database contains all required tables, as described in models.py
# models.Base.metadata.create_all(bind=engine)
#   Now using alembic instead:
#    alembic revision --autogenerate -m "<comment>"
#    <fix auto-generated .py file, if needed>
#    alembic upgrade head

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)


@app.get("/")
async def root():
    return {"message": "Hello World! and everyone else"}


