# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and configure Poetry
RUN pip install --upgrade pip
RUN pip config set global.index-url https://pypi.org/simple
RUN pip install poetry --default-timeout=100

# Copy Poetry configuration files first to leverage Docker's layer caching
COPY pyproject.toml poetry.lock /app/

# Install project dependencies using Poetry
RUN poetry install --no-root --with dev

# Copy project files into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8001

# Command to run the FastAPI application
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8001"]
