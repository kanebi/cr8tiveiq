# CR8TIVEIQ Website

A modern digital agency website built with Django CMS and PostgreSQL.

## Project Structure

```
cr8tiveiq/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   ├── portfolio/
│   ├── services/
│   ├── blog/
│   ├── contact/
│   └── analytics/
├── templates/
│   ├── base.html
│   ├── includes/
│   ├── core/
│   ├── portfolio/
│   ├── services/
│   ├── blog/
│   └── contact/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Create Database

```bash
# Make sure PostgreSQL is running
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Apps Overview

### Core App
- Home page
- About page
- Base templates and utilities

### Portfolio App
- Portfolio projects listing
- Portfolio detail view
- Category filtering

### Services App
- Services listing
- Service detail view

### Blog App
- Blog articles listing
- Blog article detail view
- Category filtering

### Contact App
- Contact form
- Newsletter subscription
- Contact inquiries management

### Analytics App
- Event tracking
- Analytics dashboard

## Database Models

- **PortfolioProject**: Portfolio projects with images and videos
- **Service**: Services offered by the agency
- **BlogArticle**: Blog articles with publishing workflow
- **ContactInquiry**: Contact form submissions
- **NewsletterSubscriber**: Newsletter subscribers
- **AnalyticsEvent**: Tracked analytics events

## Features

- Responsive design (mobile-first)
- SEO optimized
- Analytics integration
- Contact form with validation
- Newsletter subscription
- Admin interface for content management
- Image optimization
- Smooth animations and transitions

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface

Access the admin interface at `http://localhost:8000/admin/`

## Deployment

Production runs on Railway. Uploaded images are stored on Google Cloud Storage.

Set these on the Railway service (leave `USE_GCS=False` locally):

```
USE_GCS=True
GS_MEDIA_URL=https://storage.googleapis.com/cr8tiveiq-media/media/
```

The bucket name is read from that URL. A public bucket is enough to render images. For admin uploads, set `GCS_CREDENTIALS_JSON` to the service-account JSON object itself (one line), not a file path.

See `DEPLOYMENT.md` for production deployment instructions.

## License

All rights reserved © 2024 CR8TIVEIQ
