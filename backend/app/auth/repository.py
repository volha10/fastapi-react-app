from pymongo import errors
from pymongo.asynchronous.database import AsyncDatabase


class UserRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db["users"]

    async def create(self, user_data: dict):
        try:
            insert_result = await self.collection["users"].insert_one(user_data)

            new_user = await self.collection["users"].find_one(
                {"_id": insert_result.inserted_id}
            )

            print(f"New user {new_user} created successfully")
        except errors.DuplicateKeyError:
            return None

        return new_user
