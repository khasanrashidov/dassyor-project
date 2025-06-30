from flask import Blueprint, jsonify

from config.logging_config import get_logger
from services.current_user_service import CurrentUserService, require_auth, require_role
from services.user_service import UserService

# Create logger for this module
logger = get_logger(__name__)

# Create Blueprint for user routes
users_bp = Blueprint("users", __name__, url_prefix="/api/users")

user_service = UserService()


@users_bp.route("/", methods=["GET"])
@require_role("Admin")
def get_users():
    """Get all users"""
    logger.info("Get users endpoint called")

    try:
        # Get all users
        result = user_service.get_all_users()

        if not result.is_success:
            logger.warning(f"Get users failed: {result.message}")
            return (
                jsonify(
                    {
                        "isSuccess": result.is_success,
                        "message": result.message,
                        "errors": result.errors,
                    }
                ),
                400,
            )

        logger.info("Users retrieved successfully")
        return (
            jsonify(
                {
                    "isSuccess": result.is_success,
                    "message": result.message,
                    "data": result.data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in get users endpoint: {str(e)}")
        return (
            jsonify(
                {
                    "isSuccess": False,
                    "message": "Internal server error",
                    "errors": ["An unexpected error occurred"],
                }
            ),
            500,
        )


@users_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user():
    """Get current user information - protected route"""
    logger.info("Get current user endpoint called")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Get user information
        result = user_service.get_current_user_info(current_user)

        if not result.is_success:
            logger.warning(f"Get current user failed: {result.message}")
            return (
                jsonify(
                    {
                        "isSuccess": result.is_success,
                        "message": result.message,
                        "errors": result.errors,
                    }
                ),
                400,
            )

        logger.info("Current user information retrieved successfully")
        return (
            jsonify(
                {
                    "isSuccess": result.is_success,
                    "message": result.message,
                    "data": result.data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in get current user endpoint: {str(e)}")
        return (
            jsonify(
                {
                    "isSuccess": False,
                    "message": "Internal server error",
                    "errors": ["An unexpected error occurred"],
                }
            ),
            500,
        )
