from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field

StrObjectId = Annotated[str, BeforeValidator(str)]


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserSignin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    # validation_alias = read from DB as '_id'
    # field name 'id' = output to JSON as 'id'
    id: StrObjectId = Field(validation_alias="_id")
    name: str
    email: EmailStr

    password: str

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserOut(BaseModel):
    id: StrObjectId = Field(validation_alias="_id")
    name: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserSigninOut(BaseModel):
    access_token: str
