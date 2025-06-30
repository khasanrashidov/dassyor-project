import datetime
import uuid

from config.database_config import db
from models.project.phase_status import PhaseStatus


class ProjectPhase(db.Model):
    """ProjectPhase model representing a project's progress through a specific phase"""

    __tablename__ = "project_phases"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False
    )
    phase_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("phases.id"), nullable=False
    )
    status = db.Column(
        db.Enum(PhaseStatus), nullable=False, default=PhaseStatus.IN_PROGRESS
    )
    data = db.Column(
        db.JSON, nullable=True
    )  # Store phase-specific data (links, chat messages, etc.)
    started_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    # Relationships
    project = db.relationship("Project", back_populates="project_phases")
    phase = db.relationship("Phase", back_populates="project_phases")

    # Unique constraint to ensure one phase per project
    __table_args__ = (
        db.UniqueConstraint("project_id", "phase_id", name="uq_project_phase"),
    )

    def __repr__(self):
        return f"<ProjectPhase {self.project_id} - {self.phase_id}>"

    def to_dict(self):
        """Convert project phase object to dictionary"""
        return {
            "id": str(self.id),
            "projectId": str(self.project_id),
            "phaseId": str(self.phase_id),
            "status": self.status.value,
            "data": self.data,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "phase": self.phase.to_dict() if self.phase else None,
        }

    def complete(self):
        """Mark phase as completed"""
        self.status = PhaseStatus.COMPLETED
        self.completed_at = datetime.datetime.utcnow()

    def reopen(self):
        """Reopen a completed phase"""
        self.status = PhaseStatus.IN_PROGRESS
        self.completed_at = None

    def update_data(self, data):
        """Update phase data"""
        if self.data is None:
            self.data = {}
        self.data.update(data)
