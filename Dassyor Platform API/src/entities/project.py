import datetime
import uuid

from config.database_config import db
from models.project.project_status import ProjectStatus


class Project(db.Model):
    """Project model representing a user's project"""

    __tablename__ = "projects"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(ProjectStatus), nullable=False, default=ProjectStatus.IN_PROGRESS
    )
    start_date = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    end_date = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Foreign key to the owner (creator) of the project
    owner_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    # Relationship with the owner
    owner = db.relationship(
        "User", foreign_keys=[owner_id], back_populates="owned_projects"
    )

    # Relationship with collaborators through the association table
    collaborators = db.relationship(
        "User",
        secondary="project_collaborators",
        back_populates="collaborated_projects",
    )

    # Relationship with invitations
    invitations = db.relationship("ProjectInvitation", back_populates="project")

    # Relationship with project phases
    project_phases = db.relationship("ProjectPhase", back_populates="project")

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self):
        """Convert project object to dictionary (useful for JSON serialization)"""
        # Get only active collaborators
        from entities.project_collaborator import ProjectCollaborator

        active_collaborators = (
            db.session.query(ProjectCollaborator)
            .filter_by(project_id=self.id, is_active=True)
            .all()
        )
        active_collaborator_ids = [
            str(collab.user_id) for collab in active_collaborators
        ]

        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "isDeleted": self.is_deleted,
            "ownerId": str(self.owner_id),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "deletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "collaborators": active_collaborator_ids,
        }

    def soft_delete(self):
        """Soft delete the project by marking as deleted and setting deleted_at timestamp"""
        self.is_deleted = True
        self.deleted_at = datetime.datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted project"""
        self.is_deleted = False
        self.deleted_at = None

    def complete(self):
        """Mark project as completed and set end date"""
        self.status = ProjectStatus.COMPLETED
        self.end_date = datetime.datetime.utcnow()

    def reopen(self):
        """Reopen a completed project"""
        self.status = ProjectStatus.IN_PROGRESS
        self.end_date = None
