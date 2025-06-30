import uuid

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from config.logging_config import get_logger
from models.project.create_project_request import CreateProjectRequest
from models.project.invite_collaborator_request import InviteCollaboratorRequest
from models.project.update_project_request import UpdateProjectRequest
from services.current_user_service import CurrentUserService, require_auth
from services.project_service import ProjectService

# Create logger for this module
logger = get_logger(__name__)

# Create Blueprint for project routes
projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")

project_service = ProjectService()


@projects_bp.route("/", methods=["POST"])
@require_auth
def create_project():
    """Create a new project"""
    logger.info("Create project endpoint called")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Create project failed: no JSON data provided")
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
            create_request = CreateProjectRequest(**data)
        except ValidationError as e:
            logger.warning(f"Create project validation failed: {str(e)}")
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

        # Create project
        result = project_service.create_project(
            name=create_request.name,
            description=create_request.description,
            owner_id=current_user.user_id,
        )

        if not result.is_success:
            logger.warning(f"Create project failed: {result.message}")
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

        logger.info("Project created successfully")
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 201

    except Exception as e:
        logger.error(f"Unexpected error in create project endpoint: {str(e)}")
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


@projects_bp.route("/", methods=["GET"])
@require_auth
def get_user_projects():
    """Get all projects for the current user"""
    logger.info("Get user projects endpoint called")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Get projects
        result = project_service.get_user_projects(
            current_user.user_id, current_user.role
        )

        if not result.is_success:
            logger.warning(f"Get user projects failed: {result.message}")
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

        logger.info("User projects retrieved successfully")
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
        logger.error(f"Unexpected error in get user projects endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>", methods=["GET"])
@require_auth
def get_user_project(project_id):
    """Get project by ID"""
    logger.info(f"Get project endpoint called for project: {project_id}")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Validate project ID
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            logger.warning(f"Invalid project ID format: {project_id}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid project ID",
                        "errors": ["Project ID must be a valid UUID"],
                    }
                ),
                400,
            )

        # Get project
        result = project_service.get_project(
            project_uuid, current_user.user_id, current_user.role
        )

        if not result.is_success:
            logger.warning(f"Get project failed: {result.message}")
            return (
                jsonify(
                    {
                        "isSuccess": result.is_success,
                        "message": result.message,
                        "errors": result.errors,
                    }
                ),
                404,
            )

        logger.info(f"Project retrieved successfully: {project_id}")
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
        logger.error(f"Unexpected error in get project endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>", methods=["PUT"])
@require_auth
def update_project(project_id):
    """Update project details"""
    logger.info(f"Update project endpoint called for project: {project_id}")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Validate project ID
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            logger.warning(f"Invalid project ID format: {project_id}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid project ID",
                        "errors": ["Project ID must be a valid UUID"],
                    }
                ),
                400,
            )

        # Get and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Update project failed: no JSON data provided")
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
            update_request = UpdateProjectRequest(**data)
        except ValidationError as e:
            logger.warning(f"Update project validation failed: {str(e)}")
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

        # Update project
        result = project_service.update_project(
            project_id=project_uuid,
            user_id=current_user.user_id,
            user_role=current_user.role,
            name=update_request.name,
            description=update_request.description,
            status=update_request.status,
        )

        if not result.is_success:
            logger.warning(f"Update project failed: {result.message}")
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

        logger.info(f"Project updated successfully: {project_id}")
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
        logger.error(f"Unexpected error in update project endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>", methods=["DELETE"])
@require_auth
def delete_project(project_id):
    """Delete a project"""
    logger.info(f"Delete project endpoint called for project: {project_id}")

    try:
        # Get current user
        current_user = CurrentUserService()

        # Validate project ID
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            logger.warning(f"Invalid project ID format: {project_id}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid project ID",
                        "errors": ["Project ID must be a valid UUID"],
                    }
                ),
                400,
            )

        # Delete project
        result = project_service.delete_project(
            project_uuid, current_user.user_id, current_user.role
        )

        if not result.is_success:
            logger.warning(f"Delete project failed: {result.message}")
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

        logger.info(f"Project deleted successfully: {project_id}")
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in delete project endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>/collaborators/<user_id>", methods=["POST"])
@require_auth
def add_collaborator(project_id, user_id):
    """Add a collaborator to the project"""
    logger.info(
        f"Add collaborator endpoint called for project: {project_id}, user: {user_id}"
    )

    try:
        # Validate IDs
        try:
            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid ID format: project={project_id}, user={user_id}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid ID format",
                        "errors": ["Project ID and User ID must be valid UUIDs"],
                    }
                ),
                400,
            )

        # Get current user for authorization
        current_user = CurrentUserService()

        # Add collaborator
        result = project_service.add_collaborator(
            project_uuid, user_uuid, current_user.user_id, current_user.role
        )

        if not result.is_success:
            logger.warning(f"Add collaborator failed: {result.message}")
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

        logger.info(
            f"Collaborator added successfully: project={project_id}, user={user_id}"
        )
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in add collaborator endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>/collaborators/<user_id>", methods=["DELETE"])
@require_auth
def remove_collaborator(project_id, user_id):
    """Remove a collaborator from the project"""
    logger.info(
        f"Remove collaborator endpoint called for project: {project_id}, user: {user_id}"
    )

    try:
        # Validate IDs
        try:
            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid ID format: project={project_id}, user={user_id}")
            return (
                jsonify(
                    {
                        "isSuccess": False,
                        "message": "Invalid ID format",
                        "errors": ["Project ID and User ID must be valid UUIDs"],
                    }
                ),
                400,
            )

        # Get current user for authorization
        current_user = CurrentUserService()

        # Remove collaborator
        result = project_service.remove_collaborator(
            project_uuid, user_uuid, current_user.user_id, current_user.role
        )

        if not result.is_success:
            logger.warning(f"Remove collaborator failed: {result.message}")
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

        logger.info(
            f"Collaborator removed successfully: project={project_id}, user={user_id}"
        )
        return jsonify({"isSuccess": result.is_success, "message": result.message}), 200

    except Exception as e:
        logger.error(f"Unexpected error in remove collaborator endpoint: {str(e)}")
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


@projects_bp.route("/<project_id>/invite", methods=["POST"])
@require_auth
def invite_collaborator(project_id):
    """Invite a user to collaborate on the project"""
    try:
        # Get current user
        current_user = CurrentUserService()

        try:
            project_id = uuid.UUID(project_id)
        except ValueError:
            return (
                jsonify(
                    {
                        "message": "Invalid project ID",
                        "errors": ["Project ID must be a valid UUID"],
                    }
                ),
                400,
            )

        data = request.get_json()
        invite_request = InviteCollaboratorRequest(**data)

        result = project_service.invite_collaborator(
            project_id=project_id,
            inviter_id=current_user.user_id,
            email=invite_request.email,
            user_role=current_user.role,
        )

        if not result.is_success:
            return jsonify({"message": result.message, "errors": result.errors}), 400

        return jsonify({"message": result.message}), 200

    except Exception as e:
        logger.error(f"Error inviting collaborator: {str(e)}")
        return (
            jsonify({"message": "Failed to send invitation", "errors": [str(e)]}),
            500,
        )


@projects_bp.route("/invitations/accept", methods=["POST"])
def accept_invitation():
    """Accept a project collaboration invitation"""
    try:
        token = request.args.get("token")
        if not token:
            return (
                jsonify({"message": "Missing token", "errors": ["Token is required"]}),
                400,
            )

        result = project_service.accept_invitation(token)

        if not result.is_success:
            return jsonify({"message": result.message, "errors": result.errors}), 400

        # Return full response including data if it exists
        response = {"message": result.message}
        if result.data:
            response["data"] = result.data

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error accepting invitation: {str(e)}")
        return (
            jsonify({"message": "Failed to accept invitation", "errors": [str(e)]}),
            500,
        )


@projects_bp.route("/invitations/reject", methods=["POST"])
def reject_invitation():
    """Reject a project collaboration invitation"""
    try:
        token = request.args.get("token")
        if not token:
            return (
                jsonify({"message": "Missing token", "errors": ["Token is required"]}),
                400,
            )

        result = project_service.reject_invitation(token)

        if not result.is_success:
            return jsonify({"message": result.message, "errors": result.errors}), 400

        return jsonify({"message": result.message}), 200

    except Exception as e:
        logger.error(f"Error rejecting invitation: {str(e)}")
        return (
            jsonify({"message": "Failed to reject invitation", "errors": [str(e)]}),
            500,
        )
