# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Install pip dependencies
RUN pip install --upgrade pip
RUN pip config set global.index-url https://pypi.org/simple
RUN pip install --default-timeout=100 poetry


# Install project dependencies using Poetry
RUN poetry install --no-root  --with dev


# Copy project files
COPY . .

# Expose the port FastAPI is running on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]