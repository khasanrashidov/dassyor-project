from functools import wraps
from typing import Optional

import jwt
from flask import current_app, request

from config.logging_config import get_logger
from entities.user import User

# Create logger for this module
logger = get_logger(__name__)


class CurrentUserService:
    def __init__(self):
        self._user = None

    @property
    def user_id(self) -> Optional[str]:
        """Get the current user's ID from the JWT token"""
        try:
            token = self._get_token_from_header()
            if not token:
                logger.warning("No token found in request")
                return None
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
                issuer=current_app.config["JWT_ISSUER"],
                audience=current_app.config["JWT_AUDIENCE"],
            )
            user_id = payload.get("sub")
            logger.debug(f"Decoded user_id from token: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            return None

    @property
    def user_email(self) -> Optional[str]:
        """Get the current user's email from the database"""
        user = self.get_current_user()
        return user.email if user else None

    @property
    def username(self) -> Optional[str]:
        """Get the current user's username from the database"""
        user = self.get_current_user()
        return user.username if user else None

    @property
    def role(self) -> Optional[str]:
        """Get the current user's role from the JWT token"""
        try:
            token = self._get_token_from_header()
            if not token:
                return None
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
                issuer=current_app.config["JWT_ISSUER"],
                audience=current_app.config["JWT_AUDIENCE"],
            )
            return payload.get("role")
        except Exception:
            return None

    @property
    def preferred_name(self) -> Optional[str]:
        """Get the current user's preferred name from the database"""
        user = self.get_current_user()
        return user.preferred_name if user else None

    @property
    def first_name(self) -> Optional[str]:
        """Get the current user's first name from the database"""
        user = self.get_current_user()
        return user.first_name if user else None

    @property
    def last_name(self) -> Optional[str]:
        """Get the current user's last name from the database"""
        user = self.get_current_user()
        return user.last_name if user else None

    @property
    def is_authenticated(self) -> bool:
        """Check if the current user is authenticated"""
        return self.user_id is not None

    def _get_token_from_header(self) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        logger.debug(f"Authorization header: {auth_header}")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Invalid or missing Authorization header")
            return None
        token = auth_header.split(" ")[1]
        logger.debug(
            f"Extracted token: {token[:10]}..."
        )  # Only log first 10 chars for security
        return token

    def get_current_user(self) -> Optional[User]:
        """Get the current user object from the database"""
        if not self.user_id:
            return None

        if self._user is None:
            self._user = User.query.filter_by(id=self.user_id, is_deleted=False).first()

        return self._user


def require_auth(f):
    """Decorator to require authentication for a route"""

    @wraps(f)
    def decorated(*args, **kwargs):
        logger.debug("Checking authentication for protected route")
        current_user_service = CurrentUserService()
        if not current_user_service.is_authenticated:
            logger.warning("Authentication failed: user is not authenticated")
            return {"message": "Authentication required"}, 401
        logger.debug(
            f"Authentication successful for user: {current_user_service.user_id}"
        )
        return f(*args, **kwargs)

    return decorated


def require_role(role: str):
    """Decorator to require a specific role for a route"""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user_service = CurrentUserService()
            if not current_user_service.is_authenticated:
                return {"message": "Authentication required"}, 401
            if current_user_service.role != role:
                return {"message": "Insufficient permissions"}, 403
            return f(*args, **kwargs)

        return decorated

    return decorator
