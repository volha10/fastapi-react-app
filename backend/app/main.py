from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient

from .auth import controllers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncMongoClient("mongodb://localhost:27020") as client:
        await client.admin.command("ping")
        app.state.db = client.get_database("auth_db")
        # await app.state.db["users"].drop()
        await app.state.db["users"].create_index("email", unique=True)
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(controllers.router)


@app.get("/")
def ping():
    return "Alive"
