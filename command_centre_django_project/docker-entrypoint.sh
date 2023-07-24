#!/bin/bash

sleep 10 && 

# Apply database migrations (if applicable)
python manage.py migrate

# Collect static files (if applicable)
python manage.py collectstatic --noinput

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
