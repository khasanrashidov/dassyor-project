from flask import Blueprint, request, jsonify

from config.logging_config import get_logger
from models.base_response import BaseResponse
from services.phase_service import PhaseService
from services.project_service import ProjectService
from services.current_user_service import CurrentUserService, require_auth, require_role

logger = get_logger(__name__)

phases_bp = Blueprint("phases", __name__)


@phases_bp.route("/seed", methods=["POST"])
@require_auth
@require_role("Admin")
def seed_phases():
    """Seed the database with default phases"""
    try:
        phases = PhaseService.seed_default_phases()

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message=f"Successfully seeded {len(phases)} phases",
                    data=[phase.to_dict() for phase in phases],
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error seeding phases: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False, message="Failed to seed phases", errors=[str(e)]
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/", methods=["GET"])
@require_auth
def get_all_phases():
    """Get all available phases"""
    try:
        phases = PhaseService.get_all_phases()

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Phases retrieved successfully",
                    data=[phase.to_dict() for phase in phases],
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving phases: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to retrieve phases",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>", methods=["GET"])
@require_auth
def get_project_phases(project_id: str):
    """Get all phases for a specific project"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        project_phases = PhaseService.get_project_phases(project_id)

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Project phases retrieved successfully",
                    data=[phase.to_dict() for phase in project_phases],
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving project phases: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to retrieve project phases",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>/current", methods=["GET"])
@require_auth
def get_current_phase(project_id: str):
    """Get the current active phase for a project"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        current_phase = PhaseService.get_current_phase(project_id)

        if not current_phase:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="No active phase found",
                        errors=["Project has no active phase"],
                    ).to_dict()
                ),
                404,
            )

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Current phase retrieved successfully",
                    data=current_phase.to_dict(),
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving current phase: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to retrieve current phase",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>/phases/<phase_id>/start", methods=["POST"])
@require_auth
def start_phase(project_id: str, phase_id: str):
    """Start a specific phase for a project"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        started_phase = PhaseService.start_phase(project_id, phase_id)

        if not started_phase:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="Phase not found or cannot be started",
                        errors=[
                            "Phase with provided ID does not exist for this project or is not in NOT_STARTED status"
                        ],
                    ).to_dict()
                ),
                404,
            )

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Phase started successfully",
                    data=started_phase.to_dict(),
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error starting phase: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to start phase",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>/phases/<phase_id>/complete", methods=["POST"])
@require_auth
def complete_phase(project_id: str, phase_id: str):
    """Complete a specific phase for a project"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        completed_phase = PhaseService.complete_phase(project_id, phase_id)

        if not completed_phase:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="Phase not found",
                        errors=[
                            "Phase with provided ID does not exist for this project"
                        ],
                    ).to_dict()
                ),
                404,
            )

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Phase completed successfully",
                    data=completed_phase.to_dict(),
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error completing phase: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to complete phase",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>/phases/<phase_id>/data", methods=["PUT"])
@require_auth
def update_phase_data(project_id: str, phase_id: str):
    """Update data for a specific phase"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="Invalid request",
                        errors=["Request body is required"],
                    ).to_dict()
                ),
                400,
            )

        updated_phase = PhaseService.update_phase_data(project_id, phase_id, data)

        if not updated_phase:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="Phase not found",
                        errors=[
                            "Phase with provided ID does not exist for this project"
                        ],
                    ).to_dict()
                ),
                404,
            )

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Phase data updated successfully",
                    data=updated_phase.to_dict(),
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error updating phase data: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to update phase data",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )


@phases_bp.route("/projects/<project_id>/next", methods=["POST"])
@require_auth
def move_to_next_phase(project_id: str):
    """Move to the next phase for a project"""
    try:
        current_user_service = CurrentUserService()
        current_user = current_user_service.user_id
        user_role = current_user_service.role

        # Check if user has access to the project
        project_service = ProjectService()
        project_response = project_service.get_project(
            project_id, current_user, user_role
        )

        if not project_response.is_success:
            return jsonify(project_response.to_dict()), 404

        next_phase = PhaseService.move_to_next_phase(project_id)

        if not next_phase:
            return (
                jsonify(
                    BaseResponse(
                        is_success=False,
                        message="No next phase available",
                        errors=["Project is already at the final phase"],
                    ).to_dict()
                ),
                404,
            )

        return (
            jsonify(
                BaseResponse(
                    is_success=True,
                    message="Moved to next phase successfully",
                    data=next_phase.to_dict(),
                ).to_dict()
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error moving to next phase: {str(e)}")
        return (
            jsonify(
                BaseResponse(
                    is_success=False,
                    message="Failed to move to next phase",
                    errors=[str(e)],
                ).to_dict()
            ),
            500,
        )
