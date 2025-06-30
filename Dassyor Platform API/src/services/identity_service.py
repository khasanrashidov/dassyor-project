import base64
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

from config.database_config import db
from config.logging_config import get_logger
from entities.user import User
from models.auth.auth_result import AuthResult
from models.auth.google_user_login_model import GoogleUserLoginModel
from models.auth.login_request import LoginRequest
from models.auth.register_request import RegisterRequest
from models.auth.reset_password_request import ResetPasswordRequest
from services.current_user_service import CurrentUserService
from services.email_service import EmailService
from services.jwt_service import JWTService

# Load environment variables
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Create logger for this module
logger = get_logger(__name__)


class IdentityService:
    def __init__(self):
        logger.info("Initializing Identity Service")
        self.email_service = EmailService()
        self.jwt_service = JWTService()
        self.google_client_id = GOOGLE_CLIENT_ID
        if not self.google_client_id:
            logger.error("GOOGLE_CLIENT_ID environment variable is missing")
            raise ValueError("GOOGLE_CLIENT_ID environment variable is required")
        logger.info("Identity Service initialized successfully")

    def _generate_unique_username(self):
        """Generate a unique username for new users"""
        username = f"user_{uuid.uuid4().hex}"
        logger.debug(f"Generated unique username: {username}")
        return username

    def _generate_email_confirmation_token(self):
        """Generate a secure email confirmation token"""
        # Generate a secure random token (32 bytes = 256 bits)
        token = secrets.token_urlsafe(32)
        logger.debug("Generated email confirmation token")
        return token

    def _encode_token_for_url(self, token: str) -> str:
        """Encode token for URL safety (similar to Base64UrlEncode in .NET)"""
        token_bytes = token.encode("utf-8")
        encoded = base64.urlsafe_b64encode(token_bytes).decode("utf-8")
        # Remove padding for URL safety (similar to .NET Base64UrlEncode)
        return encoded.rstrip("=")

    def _decode_token_from_url(self, encoded_token: str) -> str:
        """Decode token from URL (similar to Base64UrlDecode in .NET)"""
        # Add padding if needed
        padding = len(encoded_token) % 4
        if padding:
            encoded_token += "=" * (4 - padding)

        try:
            token_bytes = base64.urlsafe_b64decode(encoded_token.encode("utf-8"))
            return token_bytes.decode("utf-8")
        except Exception as e:
            logger.warning(f"Failed to decode token: {str(e)}")
            raise ValueError("Invalid token format")

    def register(self, request: RegisterRequest) -> AuthResult:
        """Register a new user and send confirmation email (no tokens returned)"""
        logger.info(f"Registration attempt for email: {request.email}")

        if not request:
            logger.warning("Registration failed: request is null")
            return AuthResult(
                message="Request cannot be null",
                is_success=False,
                errors=["Request cannot be null"],
            )

        try:
            # Check if user already exists
            logger.debug(f"Checking if user exists with email: {request.email}")
            existing_user = User.query.filter_by(email=request.email).first()
            if existing_user:
                logger.warning(
                    f"Registration failed: user already exists with email {request.email}"
                )
                now = datetime.now(timezone.utc)
                return AuthResult(
                    message="User with this email address already exists.",
                    is_success=False,
                    errors=[
                        "Could not create user. User with this email address already exists."
                    ],
                    user_id=None,
                    expiration=now,
                    refresh_token_expiration=now,
                    expires_in_seconds=0,
                    refresh_token_expires_in_seconds=0,
                )

            # Generate email confirmation token
            confirmation_token = self._generate_email_confirmation_token()
            token_expiry = datetime.now(timezone.utc) + timedelta(
                hours=24
            )  # Token expires in 24 hours

            # Create new user (email not confirmed yet)
            logger.info(f"Creating new user with email: {request.email}")
            new_user = User(
                email=request.email,
                username=self._generate_unique_username(),
                password_hash=generate_password_hash(request.password),
                role="Client",
                is_deleted=False,
                is_email_confirmed=False,  # Important: email not confirmed yet
                email_confirmation_token=confirmation_token,
                email_confirmation_token_expiry=token_expiry,
                created_at=datetime.now(timezone.utc),
            )

            # Add user to database
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User created successfully with ID: {new_user.id}")

            # Send confirmation email
            try:
                logger.debug(f"Sending confirmation email to: {request.email}")
                # Encode token for URL safety
                encoded_token = self._encode_token_for_url(confirmation_token)
                confirm_url = f"{self.email_service.client_app_url}/auth/confirm-email?userId={new_user.id}&token={encoded_token}"
                current_year = datetime.now().year

                self.email_service.send_email(
                    to_email=request.email,
                    subject="Confirm your email - Dassyor",
                    content=f"""
                    <!DOCTYPE html>
                    <html>
                    <body style="font-family: 'Google Sans', Verdana, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
                        <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                            <div style="color: #4084f4; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-bottom: 20px;">
                                <h2 style="font-size: 22px;margin-top: 0;">Welcome to Dassyor!</h2>
                            </div>

                            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                                <p style="font-size: 16px;margin-bottom: 20px;">Thank you for registering with Dassyor. To complete your registration and start using our platform, please confirm your email address by clicking the button below:</p>
                                
                                <div style="text-align: center; margin: 30px 0;">
                                    <a href='{confirm_url}' style='background-color: #4084f4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;'>Confirm email address</a>
                                </div>

                                <p style="font-size: 16px;margin-bottom: 0;">If the button doesn't work, you can also copy and paste this link into your browser:</p>
                                <p style="font-size: 14px; color: #666; word-break: break-all; margin-top: 10px;">{confirm_url}</p>
                            </div>

                            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                                <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Important Information</h3>
                                <ul style="font-size: 16px;margin-bottom: 0;padding-left: 20px;">
                                    <li>This link will expire in 24 hours</li>
                                    <li>If you didn't create an account, please ignore this email</li>
                                    <li>For security reasons, please don't share this email with anyone</li>
                                </ul>
                            </div>

                            <div style="margin-top: 20px; font-size: 12px; color: #666; text-align: center;">
                                <p>This email was sent automatically by Dassyor.</p>
                                <p>&copy; {current_year} Dassyor. All rights reserved.</p>
                                <p>Tashkent, Uzbekistan</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """,
                )
                logger.info(f"Confirmation email sent successfully to: {request.email}")
            except Exception as email_error:
                logger.error(
                    f"Failed to send confirmation email to {request.email}: {str(email_error)}"
                )
                # Rollback user creation if email fails
                db.session.rollback()
                return AuthResult(
                    message="Failed to send confirmation email. Please try again.",
                    is_success=False,
                    errors=["Email service unavailable"],
                )

            logger.info(
                f"User registration completed successfully for: {request.email}"
            )

            # For registration, we don't return tokens but still need to satisfy AuthResult requirements
            now = datetime.now(timezone.utc)
            return AuthResult(
                message="Registration successful! Please check your email and click the confirmation link to activate your account.",
                is_success=True,
                user_id=new_user.id,
                expiration=now,
                refresh_token_expiration=now,
                expires_in_seconds=0,
                refresh_token_expires_in_seconds=0,
            )

        except Exception as e:
            logger.error(f"User registration failed for {request.email}: {str(e)}")
            db.session.rollback()
            return AuthResult(
                message="User creation failed.", is_success=False, errors=[str(e)]
            )

    def confirm_email(self, user_id: str, token: str) -> AuthResult:
        """Confirm user's email address using the confirmation token"""
        logger.info(f"Email confirmation attempt for user ID: {user_id}")

        try:
            # Find user by ID
            user = User.query.filter_by(id=user_id, is_deleted=False).first()

            if not user:
                logger.warning(f"Email confirmation failed: invalid user ID {user_id}")
                return AuthResult(
                    message="Invalid user ID.",
                    is_success=False,
                    errors=["Invalid user ID."],
                )

            # Check if email is already confirmed
            if user.is_email_confirmed:
                logger.info(f"Email already confirmed for user: {user_id}")
                return AuthResult(
                    message="Email is already confirmed.", is_success=True
                )

            # Decode the token (similar to your .NET approach)
            try:
                decoded_token = self._decode_token_from_url(token)
            except ValueError as e:
                logger.warning(
                    f"Email confirmation failed: invalid token format for user {user_id}"
                )
                return AuthResult(
                    message="Invalid confirmation token.",
                    is_success=False,
                    errors=["Invalid confirmation token format."],
                )

            # Verify token matches and hasn't expired
            if (
                not user.email_confirmation_token
                or user.email_confirmation_token != decoded_token
            ):
                logger.warning(
                    f"Email confirmation failed: token mismatch for user {user_id}"
                )
                return AuthResult(
                    message="Invalid confirmation token.",
                    is_success=False,
                    errors=["Invalid confirmation token."],
                )

            # Check if token has expired
            if (
                user.email_confirmation_token_expiry
                and user.email_confirmation_token_expiry.replace(tzinfo=timezone.utc)
                < datetime.now(timezone.utc)
            ):
                logger.warning(
                    f"Email confirmation failed: token expired for user {user_id}"
                )
                return AuthResult(
                    message="Confirmation token has expired. Please request a new confirmation email.",
                    is_success=False,
                    errors=["Confirmation token has expired."],
                    user_id=user_id,
                    expiration=datetime.now(timezone.utc),
                    refresh_token_expiration=datetime.now(timezone.utc),
                    expires_in_seconds=0,
                    refresh_token_expires_in_seconds=0,
                )

            # Confirm the email
            user.is_email_confirmed = True
            user.email_confirmation_token = None  # Clear the token
            user.email_confirmation_token_expiry = None
            user.email_confirmed_at = datetime.now(timezone.utc)

            db.session.commit()

            logger.info(f"Email confirmed successfully for user: {user_id}")

            # Generate tokens after successful email confirmation
            access_token, access_expiry = self.jwt_service.generate_access_token(
                user_id, user.role
            )
            refresh_token, refresh_expiry = self.jwt_service.generate_refresh_token(
                user_id
            )

            return AuthResult(
                message="Email confirmed successfully! You can now log in to your account.",
                is_success=True,
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expiration=access_expiry,
                refresh_token_expiration=refresh_expiry,
                expires_in_seconds=(
                    access_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                refresh_token_expires_in_seconds=(
                    refresh_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                role=user.role,
            )

        except Exception as e:
            logger.error(f"Email confirmation failed for user {user_id}: {str(e)}")
            db.session.rollback()
            now = datetime.now(timezone.utc)
            return AuthResult(
                message="Email confirmation failed.",
                is_success=False,
                errors=[str(e)],
                user_id=user_id,
                expiration=now,
                refresh_token_expiration=now,
                expires_in_seconds=0,
                refresh_token_expires_in_seconds=0,
            )

    def login(self, request: LoginRequest) -> AuthResult:
        """Login a user and return JWT tokens"""
        logger.info(f"Login attempt for email: {request.email}")

        if not request:
            logger.warning("Login failed: request is null")
            return AuthResult(
                message="Request cannot be null",
                is_success=False,
                errors=["Request cannot be null"],
            )

        try:
            # Find user by email
            user = User.query.filter_by(email=request.email, is_deleted=False).first()

            if not user:
                logger.warning(
                    f"Login failed: user not found with email {request.email}"
                )
                return AuthResult(
                    message="Invalid email or password.",
                    is_success=False,
                    errors=["Invalid email or password."],
                )

            # Check if email is confirmed
            if not user.is_email_confirmed:
                logger.warning(f"Login failed: email not confirmed for {request.email}")
                return AuthResult(
                    message="Email is not confirmed. Please confirm your email.",
                    is_success=False,
                    errors=["Email is not confirmed."],
                )

            # Verify password
            if not check_password_hash(user.password_hash, request.password):
                logger.warning(f"Login failed: invalid password for {request.email}")
                return AuthResult(
                    message="Invalid email or password.",
                    is_success=False,
                    errors=["Invalid email or password."],
                )

            # Generate JWT tokens
            access_token, access_expiry = self.jwt_service.generate_access_token(
                str(user.id), user.role
            )
            refresh_token, refresh_expiry = self.jwt_service.generate_refresh_token(
                str(user.id)
            )

            logger.info(f"Login successful for user: {user.id}")

            return AuthResult(
                message="Login successful",
                is_success=True,
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expiration=access_expiry,
                refresh_token_expiration=refresh_expiry,
                expires_in_seconds=(
                    access_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                refresh_token_expires_in_seconds=(
                    refresh_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                role=user.role,
            )

        except Exception as e:
            logger.error(f"Login failed for {request.email}: {str(e)}")
            return AuthResult(
                message="Login failed.",
                is_success=False,
                errors=[str(e)],
            )

    def forgot_password(self, email: str) -> AuthResult:
        """Handle forgot password request"""
        logger.info(f"Forgot password attempt for email: {email}")

        try:
            # Find user by email
            user = User.query.filter_by(email=email, is_deleted=False).first()

            if not user:
                # For security reasons, return success even if user doesn't exist
                logger.info(f"No user found for forgot password request: {email}")
                return AuthResult(
                    message="If an account with this email exists, a reset link has been sent.",
                    is_success=True,
                )

            # Generate password reset token
            reset_token = (
                self._generate_email_confirmation_token()
            )  # Reuse the same token generation
            token_expiry = datetime.now(timezone.utc) + timedelta(
                hours=24
            )  # Token expires in 24 hours

            # Store the token in the user record
            user.password_reset_token = reset_token
            user.password_reset_token_expiry = token_expiry
            db.session.commit()

            # Encode token for URL safety
            encoded_token = self._encode_token_for_url(reset_token)
            reset_url = f"{self.email_service.client_app_url}/auth/reset-password?email={email}&token={encoded_token}"
            current_year = datetime.now().year

            # Send reset password email
            self.email_service.send_email(
                to_email=email,
                subject="Reset Your Password - Dassyor",
                content=f"""
                <!DOCTYPE html>
                <html>
                <body style="font-family: 'Google Sans', Verdana, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                        <div style="color: #4084f4; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-bottom: 20px;">
                            <h2 style="font-size: 22px;margin-top: 0;">Reset Your Password</h2>
                        </div>

                        <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                            <p style="font-size: 16px;margin-bottom: 20px;">We received a request to reset your password. Click the button below to create a new password:</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href='{reset_url}' style='background-color: #4084f4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;'>Reset password</a>
                            </div>

                            <p style="font-size: 16px;margin-bottom: 0;">If the button doesn't work, you can also copy and paste this link into your browser:</p>
                            <p style="font-size: 14px; color: #666; word-break: break-all; margin-top: 10px;">{reset_url}</p>
                        </div>

                        <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                            <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Important Information</h3>
                            <ul style="font-size: 16px;margin-bottom: 0;padding-left: 20px;">
                                <li>This link will expire in 24 hours</li>
                                <li>If you didn't request a password reset, please ignore this email</li>
                                <li>For security reasons, please don't share this email with anyone</li>
                            </ul>
                        </div>

                        <div style="margin-top: 20px; font-size: 12px; color: #666; text-align: center;">
                            <p>This email was sent automatically by Dassyor.</p>
                            <p>&copy; {current_year} Dassyor. All rights reserved.</p>
                            <p>Tashkent, Uzbekistan</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
            )

            logger.info(f"Password reset email sent to: {email}")
            return AuthResult(
                message="If an account with this email exists, a reset link has been sent.",
                is_success=True,
            )

        except Exception as e:
            logger.error(
                f"Failed to process forgot password request for {email}: {str(e)}"
            )
            return AuthResult(
                message="If an account with this email exists, a reset link has been sent.",
                is_success=True,  # Still return success for security reasons
            )

    def reset_password(self, request: ResetPasswordRequest) -> AuthResult:
        """Reset user's password using the reset token"""
        logger.info(f"Password reset attempt for email: {request.email}")

        try:
            # Find user by email
            user = User.query.filter_by(email=request.email, is_deleted=False).first()

            if not user:
                logger.warning(
                    f"Password reset failed: user not found with email {request.email}"
                )
                return AuthResult(
                    message="User not found.",
                    is_success=False,
                )

            # Decode the token
            try:
                decoded_token = self._decode_token_from_url(request.token)
            except ValueError as e:
                logger.warning(
                    f"Password reset failed: invalid token format for user {request.email}"
                )
                return AuthResult(
                    message="Invalid reset token.",
                    is_success=False,
                    errors=["Invalid token format."],
                )

            # Verify token matches and hasn't expired
            if (
                not user.password_reset_token
                or user.password_reset_token != decoded_token
                or not user.password_reset_token_expiry
                or user.password_reset_token_expiry.replace(tzinfo=timezone.utc)
                < datetime.now(timezone.utc)
            ):
                logger.warning(
                    f"Password reset failed: invalid or expired token for user {request.email}"
                )
                return AuthResult(
                    message="Invalid or expired reset token.",
                    is_success=False,
                    errors=["Invalid or expired token."],
                )

            # Update password
            user.password_hash = generate_password_hash(request.new_password)
            user.password_reset_token = None  # Clear the token
            user.password_reset_token_expiry = None
            db.session.commit()

            logger.info(f"Password reset successful for user: {user.id}")
            return AuthResult(
                message="Password reset successful.",
                is_success=True,
            )

        except Exception as e:
            logger.error(f"Password reset failed for {request.email}: {str(e)}")
            db.session.rollback()
            return AuthResult(
                message="Password reset failed.",
                is_success=False,
                errors=[str(e)],
            )

    def setup_password(self, request: ResetPasswordRequest) -> AuthResult:
        """Setup password for new users created through invitation"""
        logger.info(f"Password setup attempt for email: {request.email}")

        try:
            # Find user by email
            user = User.query.filter_by(email=request.email, is_deleted=False).first()

            if not user:
                logger.warning(
                    f"Password setup failed: user not found with email {request.email}"
                )
                return AuthResult(
                    message="User not found.",
                    is_success=False,
                )

            # Check if user has a password but no reset token (this means it's a real password, not temporary)
            if user.password_hash and not user.password_reset_token:
                logger.warning(
                    f"Password setup failed: user already has password for email {request.email}"
                )
                return AuthResult(
                    message="User already has a password set. Please use the password reset flow instead.",
                    is_success=False,
                    errors=["Password already exists."],
                )

            # Decode the token
            try:
                decoded_token = self._decode_token_from_url(request.token)
            except ValueError as e:
                logger.warning(
                    f"Password setup failed: invalid token format for user {request.email}"
                )
                return AuthResult(
                    message="Invalid setup token.",
                    is_success=False,
                    errors=["Invalid token format."],
                )

            # Verify token matches and hasn't expired
            if (
                not user.password_reset_token
                or user.password_reset_token != decoded_token
                or not user.password_reset_token_expiry
                or user.password_reset_token_expiry.replace(tzinfo=timezone.utc)
                < datetime.now(timezone.utc)
            ):
                logger.warning(
                    f"Password setup failed: invalid or expired token for user {request.email}"
                )
                return AuthResult(
                    message="Invalid or expired setup token.",
                    is_success=False,
                    errors=["Invalid or expired token."],
                )

            # Set up password for the first time
            user.password_hash = generate_password_hash(request.new_password)
            user.password_reset_token = None  # Clear the token
            user.password_reset_token_expiry = None
            db.session.commit()

            logger.info(f"Password setup successful for user: {user.id}")

            # Generate JWT tokens for automatic login
            access_token, access_expiry = self.jwt_service.generate_access_token(
                str(user.id), user.role
            )
            refresh_token, refresh_expiry = self.jwt_service.generate_refresh_token(
                str(user.id)
            )

            return AuthResult(
                message="Password setup successful. You are now logged in.",
                is_success=True,
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expiration=access_expiry,
                refresh_token_expiration=refresh_expiry,
                expires_in_seconds=(
                    access_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                refresh_token_expires_in_seconds=(
                    refresh_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                role=user.role,
            )

        except Exception as e:
            logger.error(f"Password setup failed for {request.email}: {str(e)}")
            db.session.rollback()
            return AuthResult(
                message="Password setup failed.",
                is_success=False,
                errors=[str(e)],
            )

    def set_preferred_name(
        self, preferred_name: str, current_user_service: CurrentUserService
    ) -> AuthResult:
        """Set user's preferred name"""
        logger.info("Setting preferred name")

        try:
            # Get current user ID
            user_id = current_user_service.user_id
            if not user_id:
                logger.warning("Set preferred name failed: user is not authorized")
                return AuthResult(
                    message="User is not authorized.",
                    is_success=False,
                )

            # Find user by ID
            user = User.query.filter_by(id=user_id, is_deleted=False).first()
            if not user:
                logger.warning(
                    f"Set preferred name failed: user not found with ID {user_id}"
                )
                return AuthResult(
                    message="User not found.",
                    is_success=False,
                    errors=["User does not exist or has been deleted."],
                )

            # Update preferred name
            user.preferred_name = preferred_name
            db.session.commit()

            logger.info(f"Preferred name updated successfully for user: {user_id}")
            return AuthResult(
                message="Preferred name updated successfully.",
                is_success=True,
            )

        except Exception as e:
            logger.error(
                f"Failed to update preferred name for user {user_id}: {str(e)}"
            )
            db.session.rollback()
            return AuthResult(
                message="Failed to update preferred name.",
                is_success=False,
                errors=[str(e)],
            )

    def login_with_google(
        self, google_user_login_model: GoogleUserLoginModel
    ) -> AuthResult:
        """Login or register a user with Google credentials"""
        logger.info(f"Google login attempt for email: {google_user_login_model.email}")

        try:
            # Find user by email
            user = User.query.filter_by(
                email=google_user_login_model.email, is_deleted=False
            ).first()

            if user and user.is_deleted:
                logger.warning(
                    f"Google login failed: user is deleted for email {google_user_login_model.email}"
                )
                return AuthResult(
                    message="User not found.",
                    is_success=False,
                    errors=["User does not exist or has been deleted."],
                )

            if not user:
                # Create new user
                logger.info(
                    f"Creating new user for Google login: {google_user_login_model.email}"
                )
                new_user = User(
                    email=google_user_login_model.email,
                    username=self._generate_unique_username(),
                    first_name=google_user_login_model.first_name,
                    last_name=google_user_login_model.last_name,
                    is_email_confirmed=True,  # Google emails are pre-verified
                    role="Client",
                    is_deleted=False,
                    created_at=datetime.now(timezone.utc),
                )

                # Add user to database
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"User created successfully with ID: {new_user.id}")
                user = new_user

            # Generate JWT tokens
            access_token, access_expiry = self.jwt_service.generate_access_token(
                str(user.id), user.role
            )
            refresh_token, refresh_expiry = self.jwt_service.generate_refresh_token(
                str(user.id)
            )

            logger.info(f"Google login successful for user: {user.id}")

            return AuthResult(
                message="Login successful",
                is_success=True,
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expiration=access_expiry,
                refresh_token_expiration=refresh_expiry,
                expires_in_seconds=(
                    access_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                refresh_token_expires_in_seconds=(
                    refresh_expiry - datetime.now(timezone.utc)
                ).total_seconds(),
                role=user.role,
            )

        except Exception as e:
            logger.error(
                f"Google login failed for {google_user_login_model.email}: {str(e)}"
            )
            db.session.rollback()
            return AuthResult(
                message="Login failed.",
                is_success=False,
                errors=[str(e)],
            )
