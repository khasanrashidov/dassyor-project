import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from config.database_config import db
from config.logging_config import get_logger
from entities.project import Project
from entities.project_collaborator import ProjectCollaborator
from entities.project_invitation import ProjectInvitation
from entities.user import User
from models.base_response import BaseResponse
from models.project.project_status import ProjectStatus
from services.email_service import EmailService
from services.phase_service import PhaseService

logger = get_logger(__name__)


class ProjectService:
    def __init__(self):
        self.email_service = EmailService()

    def create_project(
        self, name: str, description: str, owner_id: uuid.UUID
    ) -> BaseResponse:
        """Create a new project"""
        try:
            # Check if owner exists
            owner = User.query.get(owner_id)
            if not owner:
                return BaseResponse(
                    is_success=False,
                    message="Owner not found",
                    errors=["User with provided ID does not exist"],
                )

            # Create new project
            project = Project(name=name, description=description, owner_id=owner_id)

            db.session.add(project)
            db.session.flush()  # Flush to get the project ID

            # Initialize phases for the project
            try:
                PhaseService.initialize_project_phases(str(project.id))
                logger.info(f"Phases initialized for project: {project.id}")
            except Exception as phase_error:
                logger.error(
                    f"Error initializing phases for project {project.id}: {str(phase_error)}"
                )
                # Continue with project creation even if phase initialization fails

            db.session.commit()

            logger.info(f"Project created successfully: {project.id}")
            return BaseResponse(is_success=True, message="Project created successfully")

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to create project", errors=[str(e)]
            )

    def get_project(
        self, project_id: uuid.UUID, user_id: str, user_role: str = None
    ) -> BaseResponse:
        """Get project by ID (with role-based authorization)"""
        try:
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            if project.is_deleted:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project has been deleted"],
                )

            # Convert string user_id to UUID for comparison
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Invalid user ID format"],
                )

            # Admin can access any project
            if user_role == "Admin":
                return BaseResponse(
                    is_success=True,
                    message="Project retrieved successfully",
                    data=project.to_dict(),
                )

            # Check if user owns the project
            if project.owner_id == user_uuid:
                return BaseResponse(
                    is_success=True,
                    message="Project retrieved successfully",
                    data=project.to_dict(),
                )

            # Check if user is an active collaborator
            collaborator = ProjectCollaborator.query.filter_by(
                project_id=project_id, user_id=user_uuid, is_active=True
            ).first()

            if collaborator:
                return BaseResponse(
                    is_success=True,
                    message="Project retrieved successfully",
                    data=project.to_dict(),
                )

            # User has no access to this project
            return BaseResponse(
                is_success=False,
                message="Project not found",
                errors=["You don't have access to this project"],
            )

        except Exception as e:
            logger.error(f"Error retrieving project: {str(e)}")
            return BaseResponse(
                is_success=False, message="Failed to retrieve project", errors=[str(e)]
            )

    def get_user_projects(self, user_id: str, user_role: str = None) -> BaseResponse:
        """Get projects for a user (with role-based authorization)"""
        try:
            # Admin can see all projects
            if user_role == "Admin":
                all_projects = Project.query.filter_by(is_deleted=False).all()
                projects_data = [project.to_dict() for project in all_projects]

                return BaseResponse(
                    is_success=True,
                    message=f"All projects retrieved successfully ({len(all_projects)} total)",
                    data=projects_data,
                )

            # Convert string user_id to UUID for database queries
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Invalid user ID format",
                    errors=["User ID must be a valid UUID"],
                )

            # Regular users: Get owned projects
            owned_projects = Project.query.filter_by(
                owner_id=user_uuid, is_deleted=False
            ).all()

            # Regular users: Get collaborated projects
            collaborated_projects = (
                Project.query.join(ProjectCollaborator)
                .filter(
                    ProjectCollaborator.user_id == user_uuid,
                    ProjectCollaborator.is_active == True,
                    Project.is_deleted == False,
                )
                .all()
            )

            # Combine and serialize projects
            all_projects = owned_projects + collaborated_projects
            projects_data = [project.to_dict() for project in all_projects]

            return BaseResponse(
                is_success=True,
                message="Projects retrieved successfully",
                data=projects_data,
            )

        except Exception as e:
            logger.error(f"Error retrieving user projects: {str(e)}")
            return BaseResponse(
                is_success=False, message="Failed to retrieve projects", errors=[str(e)]
            )

    def update_project(
        self,
        project_id: uuid.UUID,
        user_id: str,
        user_role: str = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ProjectStatus] = None,
    ) -> BaseResponse:
        """Update project details (with role-based authorization)"""
        try:
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            if project.is_deleted:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project has been deleted"],
                )

            # Convert string user_id to UUID for comparison
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Invalid user ID format"],
                )

            # Admin can update any project, otherwise check ownership
            if user_role != "Admin" and project.owner_id != user_uuid:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Only project owners can update projects"],
                )

            # Update fields if provided
            if name is not None:
                project.name = name
            if description is not None:
                project.description = description
            if status is not None:
                project.status = status
                if status == ProjectStatus.COMPLETED:
                    project.complete()
                elif status == ProjectStatus.IN_PROGRESS:
                    project.reopen()

            db.session.commit()

            return BaseResponse(
                is_success=True,
                message="Project updated successfully",
                data=project.to_dict(),
            )

        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to update project", errors=[str(e)]
            )

    def delete_project(
        self, project_id: uuid.UUID, user_id: str, user_role: str = None
    ) -> BaseResponse:
        """Soft delete a project (with role-based authorization)"""
        try:
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            if project.is_deleted:
                return BaseResponse(
                    is_success=False,
                    message="Project already deleted",
                    errors=["Project has already been deleted"],
                )

            # Convert string user_id to UUID for comparison
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Invalid user ID format"],
                )

            # Admin can delete any project, otherwise check ownership
            if user_role != "Admin" and project.owner_id != user_uuid:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Only project owners can delete projects"],
                )

            project.soft_delete()
            db.session.commit()

            return BaseResponse(is_success=True, message="Project deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to delete project", errors=[str(e)]
            )

    def add_collaborator(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        requester_id: str,
        user_role: str = None,
    ) -> BaseResponse:
        """Add a collaborator to the project (with role-based authorization)"""
        try:
            # Check if project exists
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            # Convert requester_id string to UUID for comparison
            try:
                requester_uuid = uuid.UUID(requester_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Invalid requester ID format"],
                )

            # Admin can add collaborator to any project, otherwise check ownership
            if user_role != "Admin" and project.owner_id != requester_uuid:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Only project owners can add collaborators"],
                )

            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                return BaseResponse(
                    is_success=False,
                    message="User not found",
                    errors=["User with provided ID does not exist"],
                )

            # Check if user is already a collaborator
            existing_collab = ProjectCollaborator.query.filter_by(
                project_id=project_id, user_id=user_id
            ).first()

            if existing_collab:
                if existing_collab.is_active:
                    return BaseResponse(
                        is_success=False,
                        message="User is already a collaborator",
                        errors=[
                            "User is already an active collaborator on this project"
                        ],
                    )
                else:
                    # Reactivate existing collaboration
                    existing_collab.reactivate()
                    db.session.commit()
                    return BaseResponse(
                        is_success=True, message="Collaborator reactivated successfully"
                    )

            # Create new collaboration
            collaborator = ProjectCollaborator(project_id=project_id, user_id=user_id)

            db.session.add(collaborator)
            db.session.commit()

            return BaseResponse(
                is_success=True, message="Collaborator added successfully"
            )

        except Exception as e:
            logger.error(f"Error adding collaborator: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to add collaborator", errors=[str(e)]
            )

    def remove_collaborator(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        requester_id: str,
        user_role: str = None,
    ) -> BaseResponse:
        """Remove a collaborator from the project (with role-based authorization)"""
        try:
            # Check if project exists
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            # Convert requester_id string to UUID for comparison
            try:
                requester_uuid = uuid.UUID(requester_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Invalid requester ID format"],
                )

            # Admin can remove collaborator from any project, otherwise check ownership
            if user_role != "Admin" and project.owner_id != requester_uuid:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Only project owners can remove collaborators"],
                )

            collaborator = ProjectCollaborator.query.filter_by(
                project_id=project_id, user_id=user_id
            ).first()

            if not collaborator:
                return BaseResponse(
                    is_success=False,
                    message="Collaboration not found",
                    errors=["User is not a collaborator on this project"],
                )

            if not collaborator.is_active:
                return BaseResponse(
                    is_success=False,
                    message="Collaboration already removed",
                    errors=["User is already removed from this project"],
                )

            collaborator.deactivate()
            db.session.commit()

            return BaseResponse(
                is_success=True, message="Collaborator removed successfully"
            )

        except Exception as e:
            logger.error(f"Error removing collaborator: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False,
                message="Failed to remove collaborator",
                errors=[str(e)],
            )

    def invite_collaborator(
        self, project_id: uuid.UUID, inviter_id: str, email: str, user_role: str = None
    ) -> BaseResponse:
        """Invite a user to collaborate on a project (with role-based authorization)"""
        try:
            # Check if project exists
            project = Project.query.get(project_id)
            if not project:
                return BaseResponse(
                    is_success=False,
                    message="Project not found",
                    errors=["Project with provided ID does not exist"],
                )

            # Convert inviter_id string to UUID for comparison
            try:
                inviter_uuid = uuid.UUID(inviter_id)
            except ValueError:
                return BaseResponse(
                    is_success=False,
                    message="Invalid user ID",
                    errors=["Invalid user ID format"],
                )

            # Admin can invite to any project, otherwise check ownership
            if user_role != "Admin" and project.owner_id != inviter_uuid:
                return BaseResponse(
                    is_success=False,
                    message="Unauthorized",
                    errors=["Only project owners can invite collaborators"],
                )

            # Check if invitee email already has a user and is already a collaborator
            existing_user = User.query.filter_by(email=email, is_deleted=False).first()
            if existing_user:
                existing_collab = ProjectCollaborator.query.filter_by(
                    project_id=project_id, user_id=existing_user.id
                ).first()

                if existing_collab and existing_collab.is_active:
                    return BaseResponse(
                        is_success=False,
                        message="User is already a collaborator",
                        errors=[
                            "User is already an active collaborator on this project"
                        ],
                    )

            # Check if there's already a pending invitation
            existing_invitation = ProjectInvitation.query.filter_by(
                project_id=project_id, invitee_email=email, status="pending"
            ).first()

            if existing_invitation:
                return BaseResponse(
                    is_success=False,
                    message="Invitation already sent",
                    errors=["An invitation has already been sent to this email"],
                )

            # Generate invitation token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(
                days=7
            )  # Invitation expires in 7 days

            # Create invitation
            invitation = ProjectInvitation(
                project_id=project_id,
                inviter_id=inviter_uuid,
                invitee_email=email,
                token=token,
                expires_at=expires_at,
            )

            db.session.add(invitation)
            db.session.commit()

            # Get inviter's name
            inviter = User.query.get(inviter_uuid)
            inviter_name = inviter.preferred_name or inviter.username

            # Send invitation email
            current_year = datetime.now().year
            accept_url = f"{self.email_service.client_app_url}/projects/invitations/accept?token={token}"

            email_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: 'Google Sans', Verdana, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                    <div style="color: #4084f4; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-bottom: 20px;">
                        <h2 style="font-size: 22px;margin-top: 0;">You've been invited to collaborate on a project</h2>
                    </div>

                    <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                        <p style="font-size: 16px;margin-bottom: 20px;">Hey 👋</p>
                        <p style="font-size: 16px;margin-bottom: 20px;"><strong>{inviter_name}</strong> has invited you to collaborate on the project <strong>"{project.name}"</strong> on Dassyor.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href='{accept_url}' style='background-color: #4084f4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;'>Accept invitation</a>
                        </div>

                        <p style="font-size: 16px;margin-bottom: 0;">If you don't have a Dassyor account yet, don't worry! You'll be able to create one by clicking the button above.</p>
                    </div>

                    <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                        <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Important Information</h3>
                        <ul style="font-size: 16px;margin-bottom: 0;padding-left: 20px;">
                            <li>This invitation will expire in 7 days</li>
                            <li>If you didn't expect this invitation, please ignore this email</li>
                            <li>For security reasons, please don't share this email with anyone</li>
                        </ul>
                    </div>

                    <div style="margin-top: 20px; font-size: 12px; color: #666; text-align: center;">
                        <p>The Dassyor team</p>
                        <p>&copy; {current_year} Dassyor. All rights reserved.</p>
                        <p>Tashkent, Uzbekistan</p>
                    </div>
                </div>
            </body>
            </html>
            """

            self.email_service.send_email(
                to_email=email,
                subject=f"Project Collaboration Invitation - {project.name}",
                content=email_content,
            )

            logger.info(
                f"Collaboration invitation sent to {email} for project {project_id}"
            )
            return BaseResponse(is_success=True, message="Invitation sent successfully")

        except Exception as e:
            logger.error(f"Error sending collaboration invitation: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to send invitation", errors=[str(e)]
            )

    def accept_invitation(self, token: str) -> BaseResponse:
        """Accept a project collaboration invitation"""
        try:
            # Find invitation by token
            invitation = ProjectInvitation.query.filter_by(token=token).first()
            if not invitation:
                return BaseResponse(
                    is_success=False,
                    message="Invalid invitation",
                    errors=["Invitation not found"],
                )

            # Check if invitation is pending
            if invitation.status != "pending":
                return BaseResponse(
                    is_success=False,
                    message="Invalid invitation",
                    errors=["Invitation has already been processed"],
                )

            # Check if invitation has expired
            if invitation.is_expired():
                return BaseResponse(
                    is_success=False,
                    message="Invitation expired",
                    errors=["Invitation has expired"],
                )

            # Find or create user by email
            user = User.query.filter_by(email=invitation.invitee_email).first()
            is_new_user = False
            password_setup_token = None

            if not user:
                # Create new user with temporary password (will need to set it up)
                is_new_user = True

                # Generate password setup token
                password_setup_token = secrets.token_urlsafe(32)
                token_expiry = datetime.utcnow() + timedelta(
                    hours=24
                )  # 24 hours to set password

                # Generate a secure temporary password that user doesn't know
                # This satisfies the NOT NULL constraint but user can't log in with it
                from werkzeug.security import generate_password_hash

                temporary_password = f"temp_{secrets.token_urlsafe(32)}"
                temporary_password_hash = generate_password_hash(temporary_password)

                user = User(
                    email=invitation.invitee_email,
                    username=f"user_{uuid.uuid4().hex}",
                    is_email_confirmed=True,  # Since they're accepting an invitation
                    role="Client",
                    is_deleted=False,
                    created_at=datetime.utcnow(),
                    password_hash=temporary_password_hash,  # Temporary password to satisfy NOT NULL constraint
                    password_reset_token=password_setup_token,  # Use this for password setup
                    password_reset_token_expiry=token_expiry,
                )
                db.session.add(user)
                db.session.flush()  # Get the user ID without committing

            # Create collaboration
            collaborator = ProjectCollaborator(
                project_id=invitation.project_id, user_id=user.id
            )
            db.session.add(collaborator)

            # Mark invitation as accepted
            invitation.accept()

            db.session.commit()

            logger.info(
                f"Invitation accepted by {user.email} for project {invitation.project_id}"
            )

            # Return different response based on whether user needs to set up password
            if is_new_user:
                # Encode token for URL safety (reuse the existing method)
                from services.identity_service import IdentityService

                identity_service = IdentityService()
                encoded_token = identity_service._encode_token_for_url(
                    password_setup_token
                )

                return BaseResponse(
                    is_success=True,
                    message="Invitation accepted successfully. Please set up your password to complete registration.",
                    data={
                        "requiresPasswordSetup": True,
                        "email": user.email,
                        "passwordSetupToken": encoded_token,
                        "redirectUrl": f"{self.email_service.client_app_url}/auth/setup-password?email={user.email}&token={encoded_token}",
                    },
                )
            else:
                return BaseResponse(
                    is_success=True,
                    message="Invitation accepted successfully",
                    data={
                        "requiresPasswordSetup": False,
                        "redirectUrl": f"{self.email_service.client_app_url}/projects",
                    },
                )

        except Exception as e:
            logger.error(f"Error accepting invitation: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to accept invitation", errors=[str(e)]
            )

    def reject_invitation(self, token: str) -> BaseResponse:
        """Reject a project collaboration invitation"""
        try:
            # Find invitation by token
            invitation = ProjectInvitation.query.filter_by(token=token).first()
            if not invitation:
                return BaseResponse(
                    is_success=False,
                    message="Invalid invitation",
                    errors=["Invitation not found"],
                )

            # Check if invitation is pending
            if invitation.status != "pending":
                return BaseResponse(
                    is_success=False,
                    message="Invalid invitation",
                    errors=["Invitation has already been processed"],
                )

            # Mark invitation as rejected
            invitation.reject()
            db.session.commit()

            logger.info(f"Invitation rejected for project {invitation.project_id}")
            return BaseResponse(
                is_success=True, message="Invitation rejected successfully"
            )

        except Exception as e:
            logger.error(f"Error rejecting invitation: {str(e)}")
            db.session.rollback()
            return BaseResponse(
                is_success=False, message="Failed to reject invitation", errors=[str(e)]
            )
