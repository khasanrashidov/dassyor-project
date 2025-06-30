from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254, description="User's email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User's password"
    )
