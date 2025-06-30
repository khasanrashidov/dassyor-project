from pydantic import BaseModel, EmailStr, Field


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254, description="User's email address")
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )
