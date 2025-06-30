from flask import Flask
from config.logging_config import get_logger
from services.phase_service import PhaseService

logger = get_logger(__name__)


class SeedingService:
    """Service for handling database seeding operations"""

    @staticmethod
    def seed_all_data(app: Flask):
        """Seed all default data for the application"""
        logger.info("Starting application data seeding process")

        with app.app_context():
            try:
                # Seed phases
                SeedingService._seed_phases()

                # Future seeding operations can be added here
                # SeedingService._seed_other_data()

                logger.info("Application data seeding completed successfully")

            except Exception as e:
                logger.error(f"Failed to seed application data: {str(e)}")
                raise

    @staticmethod
    def _seed_phases():
        """Seed default phases"""
        logger.info("Starting phase seeding")
        try:
            phases = PhaseService.seed_default_phases()
            logger.info(f"Successfully seeded {len(phases)} default phases")
        except Exception as e:
            logger.error(f"Failed to seed default phases: {str(e)}")
            raise

    # Future seeding methods can be added here
    # @staticmethod
    # def _seed_other_data():
    #     """Seed other default data"""
    #     logger.info("Starting other data seeding")
    #     try:
    #         # Add other seeding logic here
    #         logger.info("Successfully seeded other data")
    #     except Exception as e:
    #         logger.error(f"Failed to seed other data: {str(e)}")
    #         raise
