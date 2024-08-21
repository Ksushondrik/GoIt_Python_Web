from datetime import date

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(max_length=150)
    phone: str = Field(min_length=10, max_length=20)
    birthday: date
    additional_data: str = Field(max_length=250)


class ContactUpdateSchema(ContactSchema):
    additional_data: str


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


