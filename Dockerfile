# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables to prevent Python from writing pyc files to disk and to ensure that scripts are run in UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

# Set working directory
WORKDIR /app

# Copy requirements file into the container at /app
COPY requirements.txt /app/

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image
COPY . /app

# Make port 8000 available for the app
EXPOSE 8000

# Create database directory if it doesn't exist and set proper permissions
RUN mkdir -p /app/db && chmod 777 /app/db

# Initialize the database
RUN python -c "from app.database import engine; from app.models.repository import Repository, Base; Base.metadata.create_all(engine)"

# Run the application
CMD ["python", "-m", "app.main"]