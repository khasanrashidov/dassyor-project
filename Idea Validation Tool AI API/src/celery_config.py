import os
from celery import Celery
from dotenv import load_dotenv

# region Load environment variables

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

# endregion

# Create Celery instance
celery_app = Celery(
    "dassyor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.tasks"],
)

# Optional Celery configuration
celery_app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": 3600,  # 1 hour
        "socket_timeout": 30,  # 30 seconds
        "socket_connect_timeout": 30,
        "retry_on_timeout": True,
    },
)
