from datetime import datetime
from typing import Optional
from uuid import UUID

from models.base_response import BaseResponse


class AuthResult(BaseResponse):
    token_type: Optional[str] = "Bearer"
    access_token: Optional[str] = ""
    refresh_token: Optional[str] = ""
    expiration: Optional[datetime] = None
    refresh_token_expiration: Optional[datetime] = None
    user_id: Optional[UUID] = None
    role: Optional[str] = ""
    expires_in_seconds: Optional[float] = None
    refresh_token_expires_in_seconds: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert the AuthResult to a dictionary for JSON serialization"""
        return {
            "isSuccess": self.is_success,
            "message": self.message,
            "errors": self.errors,
            "tokenType": self.token_type,
            "accessToken": self.access_token,
            "refreshToken": self.refresh_token,
            "expiration": self.expiration.isoformat() if self.expiration else None,
            "refreshTokenExpiration": (
                self.refresh_token_expiration.isoformat()
                if self.refresh_token_expiration
                else None
            ),
            "userId": str(self.user_id) if self.user_id else None,
            "role": self.role,
            "expiresInSeconds": self.expires_in_seconds,
            "refreshTokenExpiresInSeconds": self.refresh_token_expires_in_seconds,
        }
