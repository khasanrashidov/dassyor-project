import uuid
from typing import List, Optional, Dict, Any

from config.database_config import db
from config.logging_config import get_logger
from entities.phase import Phase
from entities.project_phase import ProjectPhase
from models.project.phase_status import PhaseStatus

logger = get_logger(__name__)


class PhaseService:
    """Service for managing project phases"""

    @staticmethod
    def get_default_phases() -> List[Dict[str, Any]]:
        """Get the default phases in order"""
        logger.debug("Getting default phases configuration")
        return [
            {
                "name": "Identify problem",
                "description": "Identify and define the core problem to solve",
                "order_index": 1,
            },
            {
                "name": "Problem scale",
                "description": "Understand the scale and scope of the problem",
                "order_index": 2,
            },
            {
                "name": "Problem impact",
                "description": "Assess the impact and consequences of the problem",
                "order_index": 3,
            },
            {
                "name": "Current solutions",
                "description": "Research and analyze existing solutions",
                "order_index": 4,
            },
            {
                "name": "Audience targeting",
                "description": "Define and identify the target audience",
                "order_index": 5,
            },
            {
                "name": "Define product",
                "description": "Define the product requirements and specifications",
                "order_index": 6,
            },
            {
                "name": "Verify demand",
                "description": "Validate market demand and product-market fit",
                "order_index": 7,
            },
            {
                "name": "Business strategy",
                "description": "Develop the business model and strategy",
                "order_index": 8,
            },
            {
                "name": "Branding",
                "description": "Create brand identity and messaging",
                "order_index": 9,
            },
            {
                "name": "Build product",
                "description": "Develop and build the actual product",
                "order_index": 10,
            },
        ]

    @staticmethod
    def seed_default_phases() -> List[Phase]:
        """Seed the database with default phases if they don't exist"""
        logger.info("Starting to seed default phases")

        existing_phases = db.session.query(Phase).all()

        if existing_phases:
            logger.info(
                f"Found {len(existing_phases)} existing phases, skipping seeding"
            )
            return existing_phases

        logger.info("No existing phases found, creating default phases")
        default_phases = PhaseService.get_default_phases()
        phases = []

        for phase_data in default_phases:
            phase = Phase(
                id=uuid.uuid4(),
                name=phase_data["name"],
                description=phase_data["description"],
                order_index=phase_data["order_index"],
                is_active=True,
            )
            phases.append(phase)
            logger.debug(f"Created phase: {phase.name} (order: {phase.order_index})")

        try:
            db.session.add_all(phases)
            db.session.commit()
            logger.info(f"Successfully seeded {len(phases)} default phases")
            return phases
        except Exception as e:
            logger.error(f"Failed to seed default phases: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_all_phases() -> List[Phase]:
        """Get all active phases ordered by order_index"""
        logger.debug("Retrieving all active phases")
        phases = (
            db.session.query(Phase)
            .filter_by(is_active=True)
            .order_by(Phase.order_index)
            .all()
        )
        logger.debug(f"Retrieved {len(phases)} active phases")
        return phases

    @staticmethod
    def get_phase_by_id(phase_id: str) -> Optional[Phase]:
        """Get a phase by its ID"""
        logger.debug(f"Retrieving phase by ID: {phase_id}")
        phase = db.session.query(Phase).filter_by(id=phase_id).first()
        if phase:
            logger.debug(f"Found phase: {phase.name}")
        else:
            logger.debug(f"Phase not found with ID: {phase_id}")
        return phase

    @staticmethod
    def get_phase_by_name(name: str) -> Optional[Phase]:
        """Get a phase by its name"""
        logger.debug(f"Retrieving phase by name: {name}")
        phase = db.session.query(Phase).filter_by(name=name).first()
        if phase:
            logger.debug(f"Found phase: {phase.name} (ID: {phase.id})")
        else:
            logger.debug(f"Phase not found with name: {name}")
        return phase

    @staticmethod
    def get_first_phase() -> Optional[Phase]:
        """Get the first phase (Identify problem)"""
        logger.debug("Retrieving first phase")
        phase = (
            db.session.query(Phase)
            .filter_by(is_active=True)
            .order_by(Phase.order_index)
            .first()
        )
        if phase:
            logger.debug(f"First phase: {phase.name}")
        else:
            logger.debug("No phases found")
        return phase

    @staticmethod
    def initialize_project_phases(project_id: str) -> List[ProjectPhase]:
        """Initialize all phases for a new project"""
        logger.info(f"Initializing phases for project: {project_id}")

        phases = PhaseService.get_all_phases()
        if not phases:
            logger.error("No phases available to initialize for project")
            raise ValueError("No phases available")

        project_phases = []

        for phase in phases:
            # Set the first phase as in progress, others as not started
            status = (
                PhaseStatus.IN_PROGRESS
                if phase.order_index == 1
                else PhaseStatus.NOT_STARTED
            )

            project_phase = ProjectPhase(
                project_id=project_id, phase_id=str(phase.id), status=status, data={}
            )
            project_phases.append(project_phase)
            logger.debug(
                f"Initialized phase '{phase.name}' for project {project_id} with status: {status.value}"
            )

        try:
            db.session.add_all(project_phases)
            db.session.commit()
            logger.info(
                f"Successfully initialized {len(project_phases)} phases for project {project_id}"
            )
            return project_phases
        except Exception as e:
            logger.error(
                f"Failed to initialize phases for project {project_id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def get_project_phases(project_id: str) -> List[ProjectPhase]:
        """Get all phases for a specific project"""
        logger.debug(f"Retrieving phases for project: {project_id}")
        project_phases = (
            db.session.query(ProjectPhase)
            .filter_by(project_id=project_id)
            .join(Phase)
            .order_by(Phase.order_index)
            .all()
        )
        logger.debug(f"Retrieved {len(project_phases)} phases for project {project_id}")
        return project_phases

    @staticmethod
    def get_project_phase(project_id: str, phase_id: str) -> Optional[ProjectPhase]:
        """Get a specific phase for a project"""
        logger.debug(f"Retrieving phase {phase_id} for project {project_id}")
        project_phase = (
            db.session.query(ProjectPhase)
            .filter_by(project_id=project_id, phase_id=phase_id)
            .first()
        )
        if project_phase:
            logger.debug(
                f"Found project phase: {project_phase.phase.name if project_phase.phase else 'Unknown'} (status: {project_phase.status.value})"
            )
        else:
            logger.debug(
                f"Project phase not found for project {project_id}, phase {phase_id}"
            )
        return project_phase

    @staticmethod
    def get_current_phase(project_id: str) -> Optional[ProjectPhase]:
        """Get the current active phase for a project"""
        logger.debug(f"Retrieving current phase for project: {project_id}")
        current_phase = (
            db.session.query(ProjectPhase)
            .filter_by(project_id=project_id, status=PhaseStatus.IN_PROGRESS)
            .join(Phase)
            .order_by(Phase.order_index)
            .first()
        )
        if current_phase:
            logger.debug(
                f"Current phase for project {project_id}: {current_phase.phase.name}"
            )
        else:
            logger.debug(f"No current phase found for project {project_id}")
        return current_phase

    @staticmethod
    def start_phase(project_id: str, phase_id: str) -> Optional[ProjectPhase]:
        """Start a specific phase for a project (change from NOT_STARTED to IN_PROGRESS)"""
        logger.info(f"Starting phase {phase_id} for project {project_id}")

        project_phase = PhaseService.get_project_phase(project_id, phase_id)
        if not project_phase:
            logger.warning(f"Phase {phase_id} not found for project {project_id}")
            return None

        if project_phase.status != PhaseStatus.NOT_STARTED:
            logger.warning(
                f"Phase {phase_id} is not in NOT_STARTED status (current: {project_phase.status.value})"
            )
            return None

        try:
            project_phase.status = PhaseStatus.IN_PROGRESS
            db.session.commit()
            logger.info(
                f"Successfully started phase '{project_phase.phase.name}' for project {project_id}"
            )
            return project_phase
        except Exception as e:
            logger.error(
                f"Failed to start phase {phase_id} for project {project_id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def complete_phase(project_id: str, phase_id: str) -> Optional[ProjectPhase]:
        """Complete a specific phase for a project"""
        logger.info(f"Completing phase {phase_id} for project {project_id}")

        project_phase = PhaseService.get_project_phase(project_id, phase_id)
        if not project_phase:
            logger.warning(f"Phase {phase_id} not found for project {project_id}")
            return None

        try:
            project_phase.complete()
            db.session.commit()
            logger.info(
                f"Successfully completed phase '{project_phase.phase.name}' for project {project_id}"
            )
            return project_phase
        except Exception as e:
            logger.error(
                f"Failed to complete phase {phase_id} for project {project_id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def update_phase_data(
        project_id: str, phase_id: str, data: Dict[str, Any]
    ) -> Optional[ProjectPhase]:
        """Update data for a specific phase"""
        logger.info(f"Updating data for phase {phase_id} in project {project_id}")
        logger.debug(f"Update data: {data}")

        project_phase = PhaseService.get_project_phase(project_id, phase_id)
        if not project_phase:
            logger.warning(f"Phase {phase_id} not found for project {project_id}")
            return None

        try:
            project_phase.update_data(data)
            db.session.commit()
            logger.info(
                f"Successfully updated data for phase '{project_phase.phase.name}' in project {project_id}"
            )
            return project_phase
        except Exception as e:
            logger.error(
                f"Failed to update data for phase {phase_id} in project {project_id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def move_to_next_phase(project_id: str) -> Optional[ProjectPhase]:
        """Move to the next phase for a project"""
        logger.info(f"Moving to next phase for project: {project_id}")

        current_phase = PhaseService.get_current_phase(project_id)
        if not current_phase:
            logger.warning(f"No current phase found for project {project_id}")
            return None

        logger.info(f"Completing current phase: {current_phase.phase.name}")
        # Complete current phase
        current_phase.complete()

        # Get next phase
        next_phase = (
            db.session.query(ProjectPhase)
            .filter_by(project_id=project_id)
            .join(Phase)
            .filter(Phase.order_index > current_phase.phase.order_index)
            .order_by(Phase.order_index)
            .first()
        )

        if next_phase:
            next_phase.status = PhaseStatus.IN_PROGRESS
            logger.info(f"Moving to next phase: {next_phase.phase.name}")
        else:
            logger.info(
                f"No next phase available for project {project_id} - project completed"
            )

        try:
            db.session.commit()
            return next_phase
        except Exception as e:
            logger.error(
                f"Failed to move to next phase for project {project_id}: {str(e)}"
            )
            db.session.rollback()
            raise
