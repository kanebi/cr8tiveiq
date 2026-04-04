# Railway Environment Variables Guide

## Required Environment Variables

Set these in your Railway project settings:

### 1. SECRET_KEY (Required)
```
SECRET_KEY=your-super-secret-key-here-change-this-in-production
```
Generate a secure key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. DEBUG (Required for Production)
```
DEBUG=False
```

### 3. ALLOWED_HOSTS (Optional - Auto-detected)
```
ALLOWED_HOSTS=your-app.railway.app,your-custom-domain.com
```
Note: Railway domain is automatically added if not set.

### 4. DATABASE_URL (Auto-provided by Railway)
Railway automatically provides this when you add a PostgreSQL database.
```
DATABASE_URL=postgresql://user:password@host:port/database
```

## Optional Environment Variables

### Email Configuration
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
```

### Redis Configuration (if using Redis)
```
USE_REDIS=True
REDIS_URL=redis://default:password@host:port
```

### Custom Domains
```
CUSTOM_DOMAINS=example.com,www.example.com
```

### Site URL
```
SITE_URL=https://your-app.railway.app
```

## Railway-Provided Variables

These are automatically set by Railway:

- `RAILWAY_PUBLIC_DOMAIN` - Your app's Railway domain
- `RAILWAY_STATIC_URL` - Static files URL
- `PORT` - Port your app should listen on
- `DATABASE_URL` - PostgreSQL connection string (if database added)

## Setting Environment Variables in Railway

### Via Dashboard:
1. Go to your project in Railway
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add variable name and value
6. Click "Add"

### Via Railway CLI:
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG="False"
```

## Checking Current Variables

### Via Dashboard:
1. Go to Variables tab
2. View all set variables

### Via CLI:
```bash
railway variables
```

## Important Notes

1. **SECRET_KEY**: Never commit this to git. Always set it as an environment variable.

2. **DEBUG**: Always set to `False` in production for security.

3. **ALLOWED_HOSTS**: Include all domains your app will be accessed from.

4. **CSRF_TRUSTED_ORIGINS**: Automatically configured based on RAILWAY_PUBLIC_DOMAIN and CUSTOM_DOMAINS.

5. **DATABASE_URL**: Automatically provided when you add a PostgreSQL database to your Railway project.

## Troubleshooting

### CSRF Error
If you see CSRF errors, ensure:
- `RAILWAY_PUBLIC_DOMAIN` is set (Railway sets this automatically)
- Your domain is in `ALLOWED_HOSTS`
- You're accessing the site via HTTPS in production

### Database Connection Error
If database connection fails:
- Ensure PostgreSQL database is added to your Railway project
- Check that `DATABASE_URL` is set
- Verify database is running in Railway dashboard

### Static Files Not Loading
If static files don't load:
- Ensure `collectstatic` ran during build (check build logs)
- Verify `STATIC_URL` and `STATIC_ROOT` in settings.py
- Check that WhiteNoise is installed and configured

### Email Not Sending
If emails aren't sending:
- Verify all email environment variables are set
- Check email credentials are correct
- For Gmail, use an App Password, not your regular password
- Ensure `EMAIL_BACKEND` is set correctly

## Example .env File for Local Development

Create a `.env` file in your project root (don't commit this):

```env
SECRET_KEY=local-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
USE_REDIS=False

# Email (optional for local dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Site
SITE_URL=http://localhost:8000
```

## Production Checklist

Before deploying to production, ensure:

- [ ] `SECRET_KEY` is set and secure
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `DATABASE_URL` is configured (PostgreSQL)
- [ ] Email settings are configured (if using email)
- [ ] Static files are collected (`collectstatic`)
- [ ] Migrations are run
- [ ] HTTPS is enabled (Railway does this automatically)
- [ ] Environment variables are not in git

## Security Best Practices

1. **Never commit sensitive data** to git
2. **Use strong SECRET_KEY** (50+ random characters)
3. **Set DEBUG=False** in production
4. **Use HTTPS** for all production traffic
5. **Regularly rotate** SECRET_KEY and passwords
6. **Limit ALLOWED_HOSTS** to only your domains
7. **Use environment variables** for all secrets
8. **Enable CSRF protection** (Django default)
9. **Keep dependencies updated** regularly
10. **Monitor logs** for security issues
