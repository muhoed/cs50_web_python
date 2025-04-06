# Wise Grocery

A web application for managing grocery inventory and shopping lists.

## Prerequisites

- Docker and Docker Compose installed
- Git

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd wisegrocery
   ```

2. Create a .env file in the wg-backend directory:
   ```bash
   cd wg-backend
   echo "SECRET_KEY='your-secret-key-here'" > .env
   ```

3. Build the Docker images:
   ```bash
   docker-compose build
   ```

4. Start the application:
   ```bash
   docker-compose up -d
   ```
   This will start all services in the correct order:
   - Start PostgreSQL and Redis
   - Wait for both services to be healthy
   - Run migrations (makemigrations and migrate)
   - Start the Django development server
   - Start Celery workers and beat scheduler

5. Create a superuser (only after the services are fully up and running):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. If you need to run additional migrations later:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

## Accessing the Application

- Backend API: http://localhost:8000
- Admin interface: http://localhost:8000/admin
- API documentation: http://localhost:8000/api/docs/

## Development

- Frontend code is in the `wg-frontend` directory
- Backend code is in the `wg-backend` directory
- API endpoints are defined in `wg-backend/wgapi/views.py`

## Troubleshooting

If you encounter database issues:
1. Stop all containers: `docker-compose down`
2. Remove the database volume: `docker volume rm wisegrocery_postgres_data`
3. Restart the services: `docker-compose up -d`

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 