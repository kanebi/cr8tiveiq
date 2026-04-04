#!/usr/bin/env python
"""Create admin user for testing."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

user, created = User.objects.get_or_create(
    username='admin',
    defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@test.com'}
)

if created:
    user.set_password('admin')
    user.save()
    print('✓ Admin user created successfully')
    print('  Username: admin')
    print('  Password: admin')
else:
    print('✓ Admin user already exists')
