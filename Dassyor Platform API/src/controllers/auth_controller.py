from flask import Blueprint, jsonify, request
from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import ValidationError

from config.logging_config import get_logger
from models.auth.forgot_password_request import ForgotPasswordRequest
from models.auth.google_login_request import GoogleLoginRequest
from models.auth.google_user_login_model import GoogleUserLoginModel
from models.auth.login_request import LoginRequest
from models.auth.register_request import RegisterRequest
from models.auth.reset_password_request import ResetPasswordRequest
from models.auth.set_preferred_name_request import SetPreferredNameRequest
from services.current_user_service import CurrentUserService, require_auth
from services.identity_service import IdentityService

# Create logger for this module
logger = get_logger(__name__)

# Create Blueprint for auth routes
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    logger.info("Registration endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Registration failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug(
            f"Registration request data received for email: {data.get('email', 'unknown')}"
        )

        # Validate request using Pydantic model
        try:
            register_request = RegisterRequest(**data)
        except ValidationError as e:
            logger.warning(f"Registration validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process registration
        identity_service = IdentityService()
        result = identity_service.register(register_request)

        if not result.is_success:
            logger.warning(
                f"Registration failed for {register_request.email}: {result.message}"
            )
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

        # Success response - NO tokens returned, user must confirm email first
        logger.info(f"Registration successful for {register_request.email}")

        return (
            jsonify({"isSuccess": result.is_success, "message": result.message}),
            201,
        )  # 201 Created

    except Exception as e:
        logger.error(f"Unexpected error in registration endpoint: {str(e)}")
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


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login a user"""
    logger.info("Login endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Login failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug(
            f"Login request data received for email: {data.get('email', 'unknown')}"
        )

        # Validate request using Pydantic model
        try:
            login_request = LoginRequest(**data)
        except ValidationError as e:
            logger.warning(f"Login validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process login
        identity_service = IdentityService()
        result = identity_service.login(login_request)

        if not result.is_success:
            logger.warning(f"Login failed for {login_request.email}: {result.message}")
            return (
                jsonify(
                    {
                        "isSuccess": result.is_success,
                        "message": result.message,
                        "errors": result.errors,
                    }
                ),
                401,  # Unauthorized
            )

        # Success response with tokens
        logger.info(f"Login successful for {login_request.email}")
        return jsonify(result.to_dict()), 200

    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}")
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


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Handle forgot password request"""
    logger.info("Forgot password endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Forgot password failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug(
            f"Forgot password request data received for email: {data.get('email', 'unknown')}"
        )

        # Validate request using Pydantic model
        try:
            forgot_password_request = ForgotPasswordRequest(**data)
        except ValidationError as e:
            logger.warning(f"Forgot password validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process forgot password request
        identity_service = IdentityService()
        result = identity_service.forgot_password(forgot_password_request.email)

        if not result.is_success:
            logger.warning(
                f"Forgot password failed for {forgot_password_request.email}: {result.message}"
            )
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

        # Success response
        logger.info(f"Forgot password email sent to {forgot_password_request.email}")
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in forgot password endpoint: {str(e)}")
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


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Handle password reset request"""
    logger.info("Reset password endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Reset password failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug(
            f"Reset password request data received for email: {data.get('email', 'unknown')}"
        )

        # Validate request using Pydantic model
        try:
            reset_password_request = ResetPasswordRequest(**data)
        except ValidationError as e:
            logger.warning(f"Reset password validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process reset password request
        identity_service = IdentityService()
        result = identity_service.reset_password(reset_password_request)

        if not result.is_success:
            logger.warning(
                f"Reset password failed for {reset_password_request.email}: {result.message}"
            )
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

        # Success response
        logger.info(f"Password reset successful for {reset_password_request.email}")
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in reset password endpoint: {str(e)}")
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


@auth_bp.route("/setup-password", methods=["POST"])
def setup_password():
    """Handle password setup for new users created through invitation"""
    logger.info("Setup password endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Setup password failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug(
            f"Setup password request data received for email: {data.get('email', 'unknown')}"
        )

        # Validate request using Pydantic model (reuse ResetPasswordRequest)
        try:
            setup_password_request = ResetPasswordRequest(**data)
        except ValidationError as e:
            logger.warning(f"Setup password validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process setup password request
        identity_service = IdentityService()
        result = identity_service.setup_password(setup_password_request)

        if not result.is_success:
            logger.warning(
                f"Setup password failed for {setup_password_request.email}: {result.message}"
            )
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

        # Success response with tokens (user is automatically logged in)
        logger.info(f"Password setup successful for {setup_password_request.email}")
        return jsonify(result.to_dict()), 200

    except Exception as e:
        logger.error(f"Unexpected error in setup password endpoint: {str(e)}")
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


@auth_bp.route("/set-preferred-name", methods=["POST"])
@require_auth
def set_preferred_name():
    """Set user's preferred name"""
    logger.info("Set preferred name endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Set preferred name failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug("Set preferred name request data received")

        # Validate request using Pydantic model
        try:
            set_preferred_name_request = SetPreferredNameRequest(**data)
        except ValidationError as e:
            logger.warning(f"Set preferred name validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Process set preferred name request
        identity_service = IdentityService()
        current_user_service = CurrentUserService()
        result = identity_service.set_preferred_name(
            set_preferred_name_request.preferred_name, current_user_service
        )

        if not result.is_success:
            logger.warning(f"Set preferred name failed: {result.message}")
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

        # Success response
        logger.info("Preferred name updated successfully")
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in set preferred name endpoint: {str(e)}")
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


@auth_bp.route("/confirm-email", methods=["GET"])
def confirm_email():
    """Confirm user's email address"""
    logger.info("Email confirmation endpoint called")

    try:
        # Get query parameters
        user_id = request.args.get("userId")
        token = request.args.get("token")

        # Validate required parameters
        if not user_id:
            logger.warning("Email confirmation failed: missing userId parameter")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "User ID is required",
                        "errors": ["Missing userId parameter"],
                    }
                ),
                400,
            )

        if not token:
            logger.warning("Email confirmation failed: missing token parameter")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Confirmation token is required",
                        "errors": ["Missing token parameter"],
                    }
                ),
                400,
            )

        logger.debug(f"Email confirmation attempt for user: {user_id}")

        # Process email confirmation
        identity_service = IdentityService()
        result = identity_service.confirm_email(user_id, token)

        if not result.is_success:
            logger.warning(
                f"Email confirmation failed for user {user_id}: {result.message}"
            )
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

        # Success response
        logger.info(f"Email confirmation successful for user: {user_id}")

        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in email confirmation endpoint: {str(e)}")
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


@auth_bp.route("/google-login", methods=["POST"])
def google_login():
    """Handle Google login request"""
    logger.info("Google login endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Google login failed: no JSON data provided")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "No data provided",
                        "errors": ["Request body must contain JSON data"],
                    }
                ),
                400,
            )

        logger.debug("Google login request data received")

        # Validate request using Pydantic model
        try:
            google_login_request = GoogleLoginRequest(**data)
        except ValidationError as e:
            logger.warning(f"Google login validation failed: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid request data",
                        "errors": [str(error) for error in e.errors()],
                    }
                ),
                400,
            )

        # Verify Google token
        try:
            identity_service = IdentityService()
            payload = id_token.verify_oauth2_token(
                google_login_request.credential,
                requests.Request(),
                identity_service.google_client_id,
            )

            # Create Google user login model
            google_user_login_model = GoogleUserLoginModel(
                email=payload["email"],
                first_name=payload.get("given_name", ""),
                last_name=payload.get("family_name", ""),
            )

            # Process Google login
            result = identity_service.login_with_google(google_user_login_model)

            if not result.is_success:
                logger.warning(f"Google login failed: {result.message}")
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

            # Success response with tokens
            logger.info(f"Google login successful for {google_user_login_model.email}")
            return jsonify(result.to_dict()), 200

        except ValueError as e:
            logger.warning(f"Invalid Google token: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid Google token. Please provide a valid Google token.",
                        "errors": ["Invalid Google token."],
                    }
                ),
                400,
            )

    except Exception as e:
        logger.error(f"Unexpected error in Google login endpoint: {str(e)}")
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
