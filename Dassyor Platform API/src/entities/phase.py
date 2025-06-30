import datetime
import uuid

from config.database_config import db


class Phase(db.Model):
    """Phase model representing predefined project phases"""

    __tablename__ = "phases"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, unique=True)
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

    # Relationship with project phases
    project_phases = db.relationship("ProjectPhase", back_populates="phase")

    def __repr__(self):
        return f"<Phase {self.name}>"

    def to_dict(self):
        """Convert phase object to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "orderIndex": self.order_index,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
