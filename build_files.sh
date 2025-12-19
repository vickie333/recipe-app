#!/bin/bash

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files for Django admin and other static assets
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "Build complete!"