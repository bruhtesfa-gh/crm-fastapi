# Dockerfile
FROM python:3.10-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY poetry.lock .
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root

# Copy project files into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the app with Uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
