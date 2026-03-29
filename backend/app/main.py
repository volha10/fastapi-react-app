from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import AsyncMongoClient

from .auth import controllers
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncMongoClient(settings.MONGO_DB_URL) as client:
        await client.admin.command("ping")
        app.state.db = client.get_database("auth_db")
        # await app.state.db["users"].drop()
        await app.state.db["users"].create_index("email", unique=True)

        # await app.state.db["refresh_tokens"].drop()
        # TTL index for refresh token's expired_at field
        await app.state.db["refresh_tokens"].create_index(
            "expired_at", expireAfterSeconds=0
        )
        await app.state.db["refresh_tokens"].create_index(
            [("user_id", 1), ("token_hash", 1)]
        )
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(controllers.router)


@app.get("/")
def ping() -> str:
    return "Alive"
