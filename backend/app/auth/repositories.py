import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import EmailStr
from pymongo import errors
from pymongo.asynchronous.database import AsyncDatabase

from app.auth.schemas import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user_data: dict) -> dict | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> User | None:
        pass


class UserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db["users"]

    async def create(self, user_data: dict) -> dict | None:
        try:
            insert_result = await self.collection.insert_one(user_data)

            new_user = await self.collection.find_one(
                {"_id": insert_result.inserted_id}
            )

            print(f"New user {new_user['_id']} created successfully")
        except errors.DuplicateKeyError:
            return None

        return new_user

    async def get_by_email(self, email: EmailStr) -> User | None:
        result = await self.collection.find_one({"email": email})
        return User(
            id=result["_id"],
            name=result["name"],
            email=result["email"],
            password_hash=result["password"],
        )

    async def get_by_id(self, id: str) -> User | None:
        result = await self.collection.find_one({"_id": id})
        return User(
            id=result["_id"],
            name=result["name"],
            email=result["email"],
            password_hash=result["password"],
        )


class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    def _hash_token(self, token: str) -> str: ...

    @abstractmethod
    async def create(
        self, user_id: str, refresh_token: str, expired_at: datetime
    ) -> None: ...

    @abstractmethod
    async def is_found_and_deleted(self, user_id: str, refresh_token: str) -> bool: ...


class MongoRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection = db["refresh_tokens"]

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create(
        self, user_id: str, refresh_token: str, expired_at: datetime
    ) -> None:
        inserted_result = await self.collection.insert_one(
            {
                "user_id": user_id,
                "token_hash": self._hash_token(refresh_token),
                "exprired_at": expired_at,
            }
        )
        new_token = await self.collection.find_one({"_id": inserted_result.inserted_id})

        print(f"New refresh token for user {new_token['user_id']} created successfully")

    async def is_found_and_deleted(self, user_id: str, refresh_token: str) -> bool:
        found_token = await self.collection.find_one_and_delete(
            {"user_id": user_id, "token_hash": self._hash_token(refresh_token)}
        )

        print(f"Token {found_token} was deleted successfully")

        return found_token is not None
