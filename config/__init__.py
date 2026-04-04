# Django config package

# Conditionally initialize Celery only if Redis is enabled
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USE_REDIS = os.getenv('USE_REDIS', 'False') == 'True'

if USE_REDIS:
    # Only import Celery if Redis is enabled
    from .celery import app as celery_app
    __all__ = ('celery_app',)
else:
    __all__ = ()
