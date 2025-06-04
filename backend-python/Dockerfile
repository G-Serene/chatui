# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents python from writing .pyc files to disc
ENV PYTHONUNBUFFERED 1         # Prevents python from buffering stdout and stderr
ENV PORT 8000                  # Default port documentation, Uvicorn below uses a fixed port

# Install system dependencies if any were needed (none for now)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on (matching Uvicorn's --port in CMD)
EXPOSE 8000

# Command to run the application
# Uvicorn will listen on port 8000 inside the container.
# This port will be mapped to a host port by Docker or Docker Compose.
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
