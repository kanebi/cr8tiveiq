# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Expose port 8080
EXPOSE 8080

# Run startup script with bash
CMD ["/bin/bash", "-c", "python manage.py migrate --no-input && python manage.py collectstatic --noinput && echo \"Starting server on port 8080\" && daphne -b 0.0.0.0 -p 8080 cariia.asgi:application"]
 