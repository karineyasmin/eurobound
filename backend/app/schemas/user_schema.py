from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBaseSchema(BaseModel):
    """
    Base schema for user data containing universal fields.
    Enforces strict email formatting via EmailStr.
    """

    email: EmailStr = Field(
        ..., description="The unique identification email for the user"
    )
    full_name: str = Field(
        ..., min_length=2, max_length=100, description="The users full name"
    )


class UserCreateSchema(UserBaseSchema):
    """
    Schema for incoming registration payloads.
    Includes validation constraints for passwords.
    """

    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Plain text password for registration",
    )


class UserResponseSchema(UserBaseSchema):
    """
    Schema for secure outgoing user responses.
    Excludes sensitive attributes like passwords
    """

    id: UUID = Field(..., description="The auto-incremented database index ID")

    class config:
        from_attributes = True
