import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

from config.logging_config import get_logger

# Load environment variables
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ISSUER = os.getenv("ISSUER")
AUDIENCE = os.getenv("AUDIENCE")
ACCESS_TOKEN_EXPIRATION_IN_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRATION_IN_MINUTES")
)
REFRESH_TOKEN_EXPIRATION_IN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_IN_DAYS"))

# Create logger for this module
logger = get_logger(__name__)


class JWTService:
    def __init__(self):
        logger.info("Initializing JWT Service")

        # Validate required environment variables
        if not JWT_SECRET_KEY:
            logger.error("JWT_SECRET_KEY environment variable is missing")
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        if len(JWT_SECRET_KEY) < 32:
            logger.error(
                f"JWT_SECRET_KEY is too short: {len(JWT_SECRET_KEY)} characters"
            )
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        if not ISSUER:
            logger.error("ISSUER environment variable is missing")
            raise ValueError("ISSUER environment variable is required")
        if not AUDIENCE:
            logger.error("AUDIENCE environment variable is missing")
            raise ValueError("AUDIENCE environment variable is required")

        self.secret_key = JWT_SECRET_KEY
        self.issuer = ISSUER
        self.audience = AUDIENCE
        self.access_token_expiration = ACCESS_TOKEN_EXPIRATION_IN_MINUTES
        self.refresh_token_expiration = REFRESH_TOKEN_EXPIRATION_IN_DAYS

        logger.info(
            f"JWT Service initialized successfully - Access token expiration: {self.access_token_expiration} minutes, Refresh token expiration: {self.refresh_token_expiration} days"
        )

    def generate_access_token(self, user_id: str, role: str) -> tuple[str, datetime]:
        """Generate a new access token"""
        logger.debug(f"Generating access token for user_id: {user_id}, role: {role}")

        if not user_id:
            logger.warning("Access token generation failed: user_id is required")
            raise ValueError("user_id is required")
        if not role:
            logger.warning("Access token generation failed: role is required")
            raise ValueError("role is required")

        expiration = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expiration
        )

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expiration,
            "iat": datetime.now(timezone.utc),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "access",
        }

        try:
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            logger.info(
                f"Access token generated successfully for user: {user_id}, expires at: {expiration}"
            )
            return token, expiration
        except Exception as e:
            logger.error(
                f"Failed to generate access token for user {user_id}: {str(e)}"
            )
            raise

    def generate_refresh_token(self, user_id: str) -> tuple[str, datetime]:
        """Generate a new refresh token"""
        logger.debug(f"Generating refresh token for user_id: {user_id}")

        if not user_id:
            logger.warning("Refresh token generation failed: user_id is required")
            raise ValueError("user_id is required")

        expiration = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expiration
        )

        payload = {
            "sub": str(user_id),
            "exp": expiration,
            "iat": datetime.now(timezone.utc),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "refresh",
        }

        try:
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            logger.info(
                f"Refresh token generated successfully for user: {user_id}, expires at: {expiration}"
            )
            return token, expiration
        except Exception as e:
            logger.error(
                f"Failed to generate refresh token for user {user_id}: {str(e)}"
            )
            raise

    def verify_token(self, token: str) -> dict:
        """Verify and decode a JWT token"""
        logger.debug("Verifying JWT token")

        if not token:
            logger.warning("Token verification failed: token is required")
            raise ValueError("Token is required")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                issuer=self.issuer,
                audience=self.audience,
            )
            user_id = payload.get("sub")
            token_type = payload.get("type", "unknown")
            logger.info(
                f"Token verified successfully for user: {user_id}, type: {token_type}"
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: invalid token - {str(e)}")
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise ValueError(f"Token verification failed: {str(e)}")

    def refresh_access_token(
        self, refresh_token: str, role: str
    ) -> tuple[str, datetime]:
        """Generate a new access token using a valid refresh token"""
        logger.debug(f"Refreshing access token with role: {role}")

        try:
            # Verify the refresh token
            payload = self.verify_token(refresh_token)

            # Check if it's actually a refresh token
            if payload.get("type") != "refresh":
                logger.warning(
                    "Token refresh failed: invalid token type, expected refresh token"
                )
                raise ValueError("Invalid token type. Expected refresh token")

            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token refresh failed: missing user ID in refresh token")
                raise ValueError("Invalid refresh token: missing user ID")

            logger.info(f"Refreshing access token for user: {user_id}")
            # Generate new access token
            return self.generate_access_token(user_id, role)

        except ValueError:
            # Re-raise validation errors (already logged)
            raise
        except Exception as e:
            logger.error(f"Failed to refresh access token: {str(e)}")
            raise ValueError(f"Failed to refresh token: {str(e)}")

    def get_user_id_from_token(self, token: str) -> str:
        """Extract user ID from a valid token"""
        logger.debug("Extracting user ID from token")

        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                logger.warning(
                    "Failed to extract user ID: token does not contain user ID"
                )
                raise ValueError("Token does not contain user ID")

            logger.debug(f"Successfully extracted user ID: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Failed to extract user ID from token: {str(e)}")
            raise

    def get_role_from_token(self, token: str) -> str:
        """Extract role from a valid access token"""
        logger.debug("Extracting role from access token")

        try:
            payload = self.verify_token(token)

            # Check if it's an access token (only access tokens have roles)
            if payload.get("type") != "access":
                logger.warning("Failed to extract role: token is not an access token")
                raise ValueError("Token is not an access token")

            role = payload.get("role")
            if not role:
                logger.warning(
                    "Failed to extract role: token does not contain role information"
                )
                raise ValueError("Token does not contain role information")

            logger.debug(f"Successfully extracted role: {role}")
            return role
        except Exception as e:
            logger.error(f"Failed to extract role from token: {str(e)}")
            raise
