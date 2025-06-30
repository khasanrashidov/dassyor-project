import datetime
import uuid

from config.database_config import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    email_confirmation_token = db.Column(db.String(255), nullable=True)
    email_confirmation_token_expiry = db.Column(db.DateTime, nullable=True)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_token_expiry = db.Column(db.DateTime, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    phone_number_verified = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    preferred_name = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="Client")
    password_hash = db.Column(db.String(255), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
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

    # Relationships with projects
    owned_projects = db.relationship(
        "Project",
        foreign_keys="Project.owner_id",
        back_populates="owner",
        lazy="dynamic",
    )

    collaborated_projects = db.relationship(
        "Project",
        secondary="project_collaborators",
        back_populates="collaborators",
    )

    # Relationship with sent invitations
    sent_invitations = db.relationship(
        "ProjectInvitation",
        foreign_keys="ProjectInvitation.inviter_id",
        back_populates="inviter",
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        """Convert user object to dictionary (useful for JSON serialization)"""
        return {
            "id": str(self.id),  # Convert UUID to string for JSON serialization
            "username": self.username,
            "email": self.email,
            "is_email_confirmed": self.is_email_confirmed,
            "email_confirmed_at": (
                self.email_confirmed_at.isoformat() if self.email_confirmed_at else None
            ),
            "phone_number": self.phone_number,
            "phone_number_verified": self.phone_number_verified,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "preferred_name": self.preferred_name,
            "bio": self.bio,
            "location": self.location,
            "role": self.role,
            "is_deleted": self.is_deleted,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }

    def soft_delete(self):
        """Soft delete the user by marking as deleted and setting deleted_at timestamp"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = datetime.datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted user"""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None

    def deactivate(self):
        """Deactivate the user account"""
        self.is_active = False

    def activate(self):
        """Activate the user account"""
        self.is_active = True

    def confirm_email(self):
        """Confirm user's email address"""
        self.is_email_confirmed = True
        self.email_confirmed_at = datetime.datetime.utcnow()
        self.email_confirmation_token = None
        self.email_confirmation_token_expiry = None

    def verify_phone(self):
        """Mark phone number as verified"""
        self.phone_number_verified = True

    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def is_admin(self):
        """Check if user has admin role"""
        return self.role.lower() == "admin"

    def is_client(self):
        """Check if user has client role"""
        return self.role.lower() == "client"
