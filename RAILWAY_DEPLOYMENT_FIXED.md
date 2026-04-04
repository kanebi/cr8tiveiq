# Railway Deployment Guide - Docker Approach

## Problem
Nixpacks was failing because pip module wasn't available in the Python environment.

## Solution
We've switched to using Docker for more reliable deployments.

## Files Created/Updated

### 1. Dockerfile (Main)
- Uses Python 3.11 slim image
- Installs system dependencies (PostgreSQL client, gcc, etc.)
- Installs Python packages
- Collects static files during build
- Runs migrations on startup

### 2. .dockerignore
- Excludes unnecessary files from Docker build
- Reduces image size and build time

### 3. railway.toml
- Updated to use DOCKERFILE builder instead of NIXPACKS
- Specifies Dockerfile path
- Includes migrate command in start command

### 4. Dockerfile.simple (Backup)
- Simpler version if the main Dockerfile has issues
- Minimal configuration

## Deployment Steps

### Option 1: Using Main Dockerfile (Recommended)

1. **Push to Git**
   ```bash
   git add .
   git commit -m "Add Docker configuration for Railway"
   git push
   ```

2. **Railway will automatically:**
   - Detect the Dockerfile
   - Build the Docker image
   - Run migrations
   - Start the application

### Option 2: Using Simple Dockerfile

If the main Dockerfile fails, rename files:
```bash
mv Dockerfile Dockerfile.backup
mv Dockerfile.simple Dockerfile
git add .
git commit -m "Use simple Dockerfile"
git push
```

### Option 3: Manual Railway Configuration

In Railway dashboard:
1. Go to your service settings
2. Under "Build", select "Dockerfile"
3. Set Dockerfile path to `Dockerfile`
4. Under "Deploy", set start command:
   ```
   python manage.py migrate --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

## Environment Variables Required

Make sure these are set in Railway:

```env
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://... (Railway provides this automatically)
ALLOWED_HOSTS=your-app.railway.app,your-custom-domain.com

# Optional
DEBUG=False
REDIS_URL=redis://... (if using Redis)
USE_REDIS=True (if using Redis)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
```

## Dockerfile Explanation

### Main Dockerfile Features:

1. **Base Image**: `python:3.11-slim`
   - Lightweight Python 3.11 image
   - Smaller size, faster builds

2. **Environment Variables**:
   - `PYTHONUNBUFFERED=1`: Real-time logs
   - `PYTHONDONTWRITEBYTECODE=1`: No .pyc files
   - `PIP_NO_CACHE_DIR=1`: Smaller image size

3. **System Dependencies**:
   - `postgresql-client`: For database operations
   - `gcc`, `python3-dev`: For compiling Python packages
   - `libpq-dev`: PostgreSQL development files

4. **Build Process**:
   - Copy requirements.txt first (better caching)
   - Install Python packages
   - Copy application files
   - Collect static files

5. **Startup**:
   - Run migrations
   - Start Gunicorn with 4 workers

## Troubleshooting

### Build Fails

**Issue**: Docker build fails
**Solution**: Check Railway build logs for specific errors

**Issue**: Missing system dependencies
**Solution**: Add them to the `apt-get install` line in Dockerfile

### Runtime Fails

**Issue**: Database connection errors
**Solution**: Ensure DATABASE_URL is set in Railway environment variables

**Issue**: Static files not loading
**Solution**: 
- Check STATIC_ROOT and STATIC_URL in settings.py
- Ensure collectstatic ran successfully in build logs

**Issue**: Port binding errors
**Solution**: Ensure using `$PORT` environment variable (Railway provides this)

### Migration Issues

**Issue**: Migrations fail on startup
**Solution**: 
- Check database connection
- Ensure migrations are committed to git
- Try running migrations manually in Railway shell

## Testing Locally with Docker

Build and run locally:
```bash
# Build image
docker build -t cr8tiveiq .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=test-key \
  -e DEBUG=True \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  cr8tiveiq
```

## Performance Optimization

### Reduce Build Time:
1. Use `.dockerignore` to exclude unnecessary files
2. Order Dockerfile commands from least to most frequently changed
3. Use multi-stage builds if needed

### Reduce Image Size:
1. Use slim Python image
2. Clean up apt cache after installing packages
3. Don't include development dependencies in production

### Improve Runtime:
1. Adjust Gunicorn workers based on Railway plan
2. Use connection pooling for database
3. Enable Redis caching if available

## Monitoring

After deployment, monitor:
- Railway deployment logs
- Application logs in Railway dashboard
- Database connection pool usage
- Response times and errors

## Rollback

If deployment fails:
```bash
# Revert to previous commit
git revert HEAD
git push

# Or rollback in Railway dashboard
# Go to Deployments → Select previous deployment → Redeploy
```

## Next Steps

1. Test the deployment
2. Set up custom domain (if needed)
3. Configure SSL (Railway provides this automatically)
4. Set up monitoring and alerts
5. Configure backups for database

## Support

If issues persist:
1. Check Railway documentation: https://docs.railway.app
2. Check Railway community: https://discord.gg/railway
3. Review Django deployment best practices
4. Check application logs for specific errors
