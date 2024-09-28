# Use official Python image as base
FROM python:3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Set the working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Install OpenTelemetry auto-instrumentation and other dependencies
#RUN poetry add opentelemetry-instrumentation opentelemetry-sdk opentelemetry-exporter-console opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-requests opentelemetry-instrumentation-sqlalchemy
RUN  opentelemetry-bootstrap -a install

# Copy the rest of the app code
#COPY . /app/
COPY ./src /app/src
COPY ./alembic.ini /app/
COPY ./src/alembic /app/src/alembic

# Expose the FastAPI port
EXPOSE 8000
RUN poetry add python-semantic-release
RUN poetry run semantic-release version

# Command to run the FastAPI application
CMD ["bash", "-c", "poetry run alembic upgrade head && opentelemetry-instrument uvicorn src.fpi.main:app --host 0.0.0.0 --port 8000"]
