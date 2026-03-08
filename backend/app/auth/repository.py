from pydantic import EmailStr
from pymongo import errors
from pymongo.asynchronous.database import AsyncDatabase


class UserRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db["users"]

    async def create(self, user_data: dict) -> dict | None:
        try:
            insert_result = await self.collection.insert_one(user_data)

            new_user = await self.collection.find_one(
                {"_id": insert_result.inserted_id}
            )

            print(f"New user {new_user} created successfully")
        except errors.DuplicateKeyError:
            return None

        return new_user

    async def get(self, email: EmailStr) -> dict | None:
        return await self.collection.find_one({"email": email})
