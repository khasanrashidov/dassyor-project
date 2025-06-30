import time
from typing import Dict, Any

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config.logging_config import get_logger
from entities.user import User
from models.base_response import BaseResponse
from models.email.email_template_models import (
    SendEmailRequest,
    BulkEmailRequest,
    PreviewEmailRequest,
    EmailTemplate,
)
from services.current_user_service import require_role, require_auth, CurrentUserService
from services.email_service import EmailService
from services.email_template_service import EmailTemplateService

# Create logger for this module
logger = get_logger(__name__)

# Create Blueprint for email routes
email_bp = Blueprint("email", __name__, url_prefix="/api/admin/email")

email_service = EmailService()
email_template_service = EmailTemplateService()


@email_bp.route("/send", methods=["POST"])
@require_role("Admin")
def send_email():
    """Send a single email with dynamic template"""
    logger.info("Send email endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Send email failed: no JSON data provided")
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

        # Validate request using Pydantic model
        try:
            send_request = SendEmailRequest(**data)
        except ValidationError as e:
            logger.warning(f"Send email validation failed: {str(e)}")
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

        # Generate HTML content from template
        try:
            html_content = email_template_service.generate_html_email(
                send_request.template
            )
        except Exception as e:
            logger.error(f"Failed to generate email template: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Failed to generate email template",
                        "errors": [str(e)],
                    }
                ),
                500,
            )

        # Send email
        success = email_service.send_email(
            to_email=send_request.to_email,
            subject=send_request.template.subject,
            content=html_content,
            is_html=True,
        )

        if success:
            logger.info(f"Email sent successfully to {send_request.to_email}")
            return (
                jsonify(
                    {
                        "isSuccess": True,
                        "message": "Email sent successfully",
                        "data": {
                            "recipient": send_request.to_email,
                            "subject": send_request.template.subject,
                        },
                    }
                ),
                200,
            )
        else:
            logger.warning(f"Failed to send email to {send_request.to_email}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Failed to send email",
                        "errors": ["Email delivery failed"],
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Unexpected error in send email endpoint: {str(e)}")
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


@email_bp.route("/bulk-send", methods=["POST"])
@require_role("Admin")
def bulk_send_email():
    """Send bulk emails with dynamic template"""
    logger.info("Bulk send email endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Bulk send email failed: no JSON data provided")
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

        # Validate request using Pydantic model
        try:
            bulk_request = BulkEmailRequest(**data)
        except ValidationError as e:
            logger.warning(f"Bulk send email validation failed: {str(e)}")
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

        # Check if we have too many recipients
        if len(bulk_request.to_emails) > 1000:
            logger.warning(
                f"Bulk send rejected: too many recipients ({len(bulk_request.to_emails)})"
            )
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Too many recipients",
                        "errors": ["Maximum 1000 recipients allowed per bulk send"],
                    }
                ),
                400,
            )

        # Generate HTML content from template
        try:
            html_content = email_template_service.generate_html_email(
                bulk_request.template
            )
        except Exception as e:
            logger.error(f"Failed to generate email template: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Failed to generate email template",
                        "errors": [str(e)],
                    }
                ),
                500,
            )

        # Send bulk emails
        results = email_service.bulk_send_email(
            to_emails=bulk_request.to_emails,
            subject=bulk_request.template.subject,
            content=html_content,
            is_html=True,
            batch_size=bulk_request.batch_size,
        )

        logger.info(
            f"Bulk email send completed. Results: {results['successful_count']}/{results['total_emails']} sent"
        )

        return (
            jsonify(
                {
                    "isSuccess": True,
                    "message": f"Bulk email send completed. {results['successful_count']}/{results['total_emails']} emails sent successfully",
                    "data": results,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in bulk send email endpoint: {str(e)}")
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


@email_bp.route("/preview", methods=["POST"])
@require_auth
def preview_email():
    """Preview an email template without sending it"""
    logger.info("Preview email endpoint called")

    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Preview email failed: no JSON data provided")
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

        # Validate request using Pydantic model
        try:
            preview_request = PreviewEmailRequest(**data)
        except ValidationError as e:
            logger.warning(f"Preview email validation failed: {str(e)}")
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

        # Generate HTML content from template
        try:
            html_content = email_template_service.generate_html_email(
                preview_request.template
            )
            metadata = email_template_service.generate_preview_metadata(
                preview_request.template
            )
        except Exception as e:
            logger.error(f"Failed to generate email preview: {str(e)}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Failed to generate email preview",
                        "errors": [str(e)],
                    }
                ),
                500,
            )

        logger.info("Email preview generated successfully")
        return (
            jsonify(
                {
                    "isSuccess": True,
                    "message": "Email preview generated successfully",
                    "data": {
                        "html_content": html_content,
                        "metadata": metadata,
                        "preview_recipient": preview_request.to_email,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in preview email endpoint: {str(e)}")
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


@email_bp.route("/templates/examples", methods=["GET"])
@require_auth
def get_template_examples():
    """Get example email templates for reference"""
    logger.info("Get template examples endpoint called")

    try:
        examples = {
            "welcome_email": {
                "subject": "Welcome to Dassyor!",
                "header": {
                    "type": "header",
                    "title": "Welcome to Dassyor!",
                    "subtitle": "Get started with your new account",
                },
                "content_blocks": [
                    {
                        "type": "text",
                        "content": "Thank you for joining Dassyor! We're excited to have you on board.",
                        "font_size": 16,
                    },
                    {
                        "type": "button",
                        "buttons": [
                            {
                                "text": "Get Started",
                                "url": "https://app.dassyor.com/dashboard",
                                "color": "#4084f4",
                            }
                        ],
                        "alignment": "center",
                    },
                    {
                        "type": "list",
                        "title": "What you can do next:",
                        "list_type": "bullet",
                        "items": [
                            {"text": "Complete your profile setup"},
                            {"text": "Create your first project"},
                            {"text": "Invite team members to collaborate"},
                        ],
                    },
                ],
                "include_default_footer": True,
            },
            "notification_email": {
                "subject": "Project Update Notification",
                "header": {
                    "type": "header",
                    "title": "Project Update",
                    "subtitle": "Important changes to your project",
                },
                "content_blocks": [
                    {
                        "type": "text",
                        "content": "Your project has been updated with new information.",
                        "font_size": 16,
                    },
                    {"type": "divider"},
                    {
                        "type": "text",
                        "content": "Changes made:",
                        "font_size": 18,
                        "color": "#4084f4",
                    },
                    {
                        "type": "list",
                        "list_type": "bullet",
                        "items": [
                            {"text": "Project description updated"},
                            {"text": "New collaborator added"},
                            {"text": "Status changed to 'In Progress'"},
                        ],
                    },
                    {"type": "spacer", "height": 30},
                    {
                        "type": "button",
                        "buttons": [
                            {
                                "text": "View Project",
                                "url": "https://app.dassyor.com/projects/123",
                                "color": "#4084f4",
                            }
                        ],
                        "alignment": "center",
                    },
                ],
                "include_default_footer": True,
            },
            "simple_text_email": {
                "subject": "Simple Text Email",
                "content_blocks": [
                    {
                        "type": "text",
                        "content": "This is a simple text email with minimal formatting.",
                        "font_size": 16,
                    },
                    {
                        "type": "text",
                        "content": "You can customize the content, colors, and alignment as needed.",
                        "font_size": 14,
                        "color": "#666",
                        "alignment": "center",
                    },
                ],
                "include_default_footer": True,
            },
        }

        logger.info("Template examples retrieved successfully")
        return (
            jsonify(
                {
                    "isSuccess": True,
                    "message": "Template examples retrieved successfully",
                    "data": {
                        "examples": examples,
                        "block_types": [
                            "text",
                            "header",
                            "button",
                            "list",
                            "image",
                            "divider",
                            "spacer",
                        ],
                        "supported_alignments": ["left", "center", "right"],
                        "supported_list_types": ["bullet", "numbered"],
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in get template examples endpoint: {str(e)}")
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


@email_bp.route("/health", methods=["GET"])
@require_auth
def email_service_health():
    """Check email service health"""
    logger.info("Email service health check endpoint called")

    try:
        # Test SMTP connection
        import smtplib

        try:
            with smtplib.SMTP_SSL(
                email_service.smtp_host, email_service.smtp_port
            ) as server:
                server.login(email_service.smtp_email, email_service.smtp_password)

            smtp_status = "healthy"
            smtp_message = "SMTP connection successful"
        except Exception as e:
            smtp_status = "unhealthy"
            smtp_message = f"SMTP connection failed: {str(e)}"
            logger.warning(f"SMTP health check failed: {str(e)}")

        health_data = {
            "email_service_status": "running",
            "smtp_status": smtp_status,
            "smtp_message": smtp_message,
            "template_service_status": "running",
            "timestamp": time.time(),
        }

        overall_status = "healthy" if smtp_status == "healthy" else "degraded"

        return (
            jsonify(
                {
                    "isSuccess": True,
                    "message": f"Email service is {overall_status}",
                    "data": health_data,
                }
            ),
            200 if overall_status == "healthy" else 503,
        )

    except Exception as e:
        logger.error(f"Unexpected error in email service health check: {str(e)}")
        return (
            jsonify(
                {
                    "isSuccess": False,
                    "message": "Email service health check failed",
                    "errors": [str(e)],
                }
            ),
            500,
        )
