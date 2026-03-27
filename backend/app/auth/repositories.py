import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

from bson.objectid import ObjectId
from pydantic import EmailStr
from pymongo import errors
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from app.auth.schemas import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user_data: dict) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> User | None:
        pass


class UserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection: AsyncCollection = db.get_collection("users")

    async def create(self, user_data: dict) -> User | None:
        try:
            insert_result = await self.collection.insert_one(user_data)

            new_user = await self.collection.find_one(
                {"_id": insert_result.inserted_id}
            )

            if not new_user:
                return None

            print(f"New user {new_user.get('_id')} created successfully")

            return self._map_to_domain(new_user)

        except errors.DuplicateKeyError:
            return None

    async def get_by_email(self, email: EmailStr) -> User | None:
        result = await self.collection.find_one({"email": email})

        return self._map_to_domain(result) if result else None

    async def get_by_id(self, id: str) -> User | None:
        result = await self.collection.find_one({"_id": ObjectId(id)})

        return self._map_to_domain(result) if result else None

    def _map_to_domain(self, document: dict) -> User:
        return User(
            id=document["_id"],
            name=document["name"],
            email=document["email"],
            password_hash=document["password"],
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

    @abstractmethod
    async def revoke_all(self, user_id: str) -> None: ...


class MongoRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, db: AsyncDatabase) -> None:
        self.collection: AsyncCollection = db.get_collection("refresh_tokens")

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

        print(f"New refresh token for user {new_token['user_id']} created successfully")  # type: ignore

    async def is_found_and_deleted(self, user_id: str, refresh_token: str) -> bool:
        found_token = await self.collection.find_one_and_delete(
            {"user_id": user_id, "token_hash": self._hash_token(refresh_token)}
        )

        if found_token:
            print(f"Token {found_token} was deleted successfully")

        return found_token is not None

    async def revoke_all(self, user_id: str) -> None:
        await self.collection.delete_many({"user_id": user_id})
