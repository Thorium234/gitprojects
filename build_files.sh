#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python3.9 manage.py collectstatic --noinput  #explain below
# The command above collects all static files from the Django app and places them in the STATIC_ROOT directory.
# This is necessary for serving static files in production environments.


# Create public directory
mkdir -p public

# Copy static files to public directory
cp -r staticfiles/* public/static/ || true
mkdir -p public/media

# Create vercel required files
echo "from school.wsgi import application" > vercel_app.py

echo "Build completed successfully!"