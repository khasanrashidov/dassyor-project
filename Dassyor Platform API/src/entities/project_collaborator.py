import datetime

from config.database_config import db


class ProjectCollaborator(db.Model):
    """Association table for project collaborators"""

    __tablename__ = "project_collaborators"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False
    )
    user_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    left_at = db.Column(db.DateTime, nullable=True)

    # Add unique constraint to prevent duplicate collaborations
    __table_args__ = (
        db.UniqueConstraint(
            "project_id", "user_id", name="unique_project_collaborator"
        ),
    )

    def __repr__(self):
        return (
            f"<ProjectCollaborator project_id={self.project_id} user_id={self.user_id}>"
        )

    def deactivate(self):
        """Deactivate the collaboration"""
        self.is_active = False
        self.left_at = datetime.datetime.utcnow()

    def reactivate(self):
        """Reactivate the collaboration"""
        self.is_active = True
        self.left_at = None
