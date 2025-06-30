from typing import List

from config.logging_config import get_logger
from entities.user import User
from models.base_response import BaseResponse
from services.current_user_service import CurrentUserService

# Create logger for this module
logger = get_logger(__name__)


class UserService:
    """Service for handling user-related operations"""

    def get_all_users(self) -> BaseResponse:
        """Get all users"""
        try:
            logger.info("Getting all users")

            users = User.query.all()
            users_data = [user.to_dict() for user in users]

            logger.info(f"Retrieved {len(users)} users")
            return BaseResponse(
                is_success=True,
                message=f"Successfully retrieved {len(users)} users",
                data={"users": users_data},
            )

        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return BaseResponse(
                is_success=False, message="Failed to retrieve users", errors=[str(e)]
            )

    def get_current_user_info(
        self, current_user_service: CurrentUserService
    ) -> BaseResponse:
        """Get current user information"""
        try:
            logger.info(
                f"Getting user info for user_id: {current_user_service.user_id}"
            )

            user_data = {
                "user_id": current_user_service.user_id,
                "email": current_user_service.user_email,
                "username": current_user_service.username,
                "role": current_user_service.role,
                "preferred_name": current_user_service.preferred_name,
                "first_name": current_user_service.first_name,
                "last_name": current_user_service.last_name,
            }

            logger.info(f"Retrieved user info for {current_user_service.user_email}")
            return BaseResponse(
                is_success=True,
                message="Successfully retrieved user information",
                data=user_data,
            )

        except Exception as e:
            logger.error(f"Error getting current user info: {str(e)}")
            return BaseResponse(
                is_success=False,
                message="Failed to retrieve user information",
                errors=[str(e)],
            )
