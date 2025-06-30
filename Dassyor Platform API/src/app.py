import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from config.database_config import init_db
from config.logging_config import get_logger, setup_logging
from controllers.auth_controller import auth_bp
from controllers.email_controller import email_bp
from controllers.phases_controller import phases_bp
from controllers.projects_controller import projects_bp
from controllers.users_controller import users_bp
from services.seeding_service import SeedingService

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ISSUER = os.getenv("ISSUER")
AUDIENCE = os.getenv("AUDIENCE")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Set up Flask app
app = Flask(__name__)

# Configure CORS
CORS(
    app,
    resources={
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

# Configure JWT settings
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ISSUER"] = ISSUER
app.config["JWT_AUDIENCE"] = AUDIENCE

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(email_bp)
app.register_blueprint(phases_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(users_bp)

# Seed default data on startup
try:
    SeedingService.seed_all_data(app)
except Exception as e:
    logger.error(f"Failed to seed application data on startup: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True)
