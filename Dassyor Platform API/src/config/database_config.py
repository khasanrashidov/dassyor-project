import os

from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config.logging_config import get_logger

# region Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Create logger for this module
logger = get_logger(__name__)


# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    logger.info("Initializing database connection...")

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    logger.info("Database and migration extensions initialized successfully")
