import datetime
import uuid

from config.database_config import db


class ProjectInvitation(db.Model):
    """Model for project collaboration invitations"""

    __tablename__ = "project_invitations"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False
    )
    inviter_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    invitee_email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, accepted, rejected
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    accepted_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    project = db.relationship("Project", back_populates="invitations")
    inviter = db.relationship(
        "User", foreign_keys=[inviter_id], back_populates="sent_invitations"
    )

    def __repr__(self):
        return f"<ProjectInvitation {self.id}>"

    def to_dict(self):
        """Convert invitation object to dictionary"""
        return {
            "id": str(self.id),
            "projectId": str(self.project_id),
            "inviterId": str(self.inviter_id),
            "inviteeEmail": self.invitee_email,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "acceptedAt": self.accepted_at.isoformat() if self.accepted_at else None,
            "rejectedAt": self.rejected_at.isoformat() if self.rejected_at else None,
        }

    def accept(self):
        """Accept the invitation"""
        self.status = "accepted"
        self.accepted_at = datetime.datetime.utcnow()

    def reject(self):
        """Reject the invitation"""
        self.status = "rejected"
        self.rejected_at = datetime.datetime.utcnow()

    def is_expired(self):
        """Check if the invitation has expired"""
        return datetime.datetime.utcnow() > self.expires_at
