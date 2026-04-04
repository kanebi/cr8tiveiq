#!/bin/bash

# Railway Deployment Script
# This script runs during deployment to set up the application

set -e  # Exit on error

echo "Starting deployment..."

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python -m pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment completed successfully!"
