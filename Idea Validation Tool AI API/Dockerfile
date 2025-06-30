# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
# Some packages might require build tools, which we can add here
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
# We use pip's --no-cache-dir flag to keep the image smaller
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# If gunicorn isn't in the requirements.txt, add it here
RUN pip install --no-cache-dir gunicorn

# Copy the application code
COPY . .

# Expose the port the application will run on
EXPOSE 8080
# EXPOSE 5000

# Define environment variable for Python to run in unbuffered mode
# This ensures that Python output is sent straight to the container logs
ENV PYTHONUNBUFFERED=1

# Command to run the application with Gunicorn
# The application will be accessible on all network interfaces
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:app", "--workers", "2", "--timeout", "120"]
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app", "--workers", "2", "--timeout", "120"]