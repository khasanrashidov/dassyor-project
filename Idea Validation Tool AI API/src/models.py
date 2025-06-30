import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# region Load environment variables

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# endregion

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for models
Base = declarative_base()


# Define the SearchTask model
class SearchTask(Base):
    __tablename__ = "search_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True, nullable=False)  # Celery task ID
    email = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    problem_statement = Column(Text)
    target_audience = Column(Text)
    analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, SUCCESS, FAILURE

    def __repr__(self):
        return f"<SearchTask(id={self.id}, email='{self.email}', query='{self.query[:30]}...', status='{self.status}')>"


# Define the RelevantPost model (for storing search results)
class RelevantPost(Base):
    __tablename__ = "relevant_posts"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False)  # Celery task ID
    title = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<RelevantPost(id={self.id}, title='{self.title[:30]}...', task_id='{self.task_id}')>"


# Create the tables in the database
# Import inspect from sqlalchemy
from sqlalchemy import inspect

# Create inspector
inspector = inspect(engine)

# Only create tables that don't exist
for table in Base.metadata.sorted_tables:
    if not inspector.has_table(table.name):
        table.create(engine)

# Create a session factory
Session = sessionmaker(bind=engine)


def get_db_session():
    """Returns a new database session."""
    return Session()
