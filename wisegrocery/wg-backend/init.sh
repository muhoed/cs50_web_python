#!/bin/bash

set -e

echo "Waiting for PostgreSQL to start..."
./wait-for-db.sh db

echo "PostgreSQL started, preparing database..."
# Make sure PostgreSQL has time to initialize completely
sleep 5

echo "Running initial migrations..."
# First, ensure the auth app tables are created
python manage.py migrate auth
# Then create content types
python manage.py migrate contenttypes
# Create initial migration files if they don't exist
python manage.py makemigrations wgapi
# Apply all migrations
python manage.py migrate

echo "Database initialization completed successfully."

# Run the command passed to the script
exec "$@" 