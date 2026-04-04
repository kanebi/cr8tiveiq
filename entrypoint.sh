#!/bin/bash
set -e

echo "==================================="
echo "Starting CR8TIVEIQ Deployment"
echo "==================================="

# Wait for database to be ready
echo "Waiting for database..."
python << END
import sys
import time
import os
import psycopg2

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("Database is ready!")
            sys.exit(0)
        else:
            print("No DATABASE_URL found, skipping database check")
            sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f"Database not ready yet (attempt {retry_count}/{max_retries}): {e}")
        time.sleep(2)

print("Could not connect to database after maximum retries")
sys.exit(1)
END

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cr8tiveiq.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "==================================="
echo "Starting Gunicorn server on port 8080..."
echo "==================================="

# Start Gunicorn on port 8080
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
