# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.0

FROM python:${PYTHON_VERSION}-slim

LABEL fly_launch_runtime="flask"

WORKDIR /code

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

# Use gunicorn with eventlet for Socket.IO support
CMD ["gunicorn", "--worker-class", "eventlet", "--workers", "1", "--bind", "0.0.0.0:8080", "--timeout", "120", "--keep-alive", "5", "--log-level", "info", "app:app"]
