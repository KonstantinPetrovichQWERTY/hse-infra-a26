# Test Task API

A FastAPI service for managing users, devices, and device measurements. The
service stores data in PostgreSQL, exposes interactive OpenAPI documentation,
and provides statistics for individual devices and users.

## Table of contents

- [Overview](#overview)
- [Quick start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Run with Docker Compose](#run-with-docker-compose)
  - [Run locally](#run-locally)
- [API](#api)
  - [Service endpoints](#service-endpoints)
  - [User endpoints](#user-endpoints)
  - [Device endpoints](#device-endpoints)
- [Database and seed data](#database-and-seed-data)
- [Testing and code quality](#testing-and-code-quality)
- [Development](#development)
  - [Project structure](#project-structure)

## Overview

The application provides:

- user and device registration;
- a many-to-many relationship between users and devices;
- device measurements with `x`, `y`, and `z` values;
- date filtering for measurements and statistics;
- per-device and aggregated per-user statistics;
- liveness, readiness, and version endpoints;
- structured request logging;
- database migrations managed with Alembic.

The application is configured through environment variables and uses
`postgresql+asyncpg` for asynchronous database access.

## Quick start

### Prerequisites

- Python 3.11 or later;
- Poetry 2.x;
- Docker and Docker Compose;
- Git.

### Configuration

Create a local environment file from the template:

```bash
# macOS/Linux
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

The `.env` file must contain PostgreSQL connection settings:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_HOST` | Yes | - | PostgreSQL host |
| `POSTGRES_USER` | Yes | - | PostgreSQL user |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `POSTGRES_DB` | Yes | - | PostgreSQL database name |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |

The `.env` file is ignored by Git. Use non-production credentials for local
development and never commit secrets.

### Run with Docker Compose

The project contains two Docker Compose files:

- `docker-compose.yml` runs the complete stack with PostgreSQL and the API;
- `docker-compose-dev.yml` runs only PostgreSQL for local API development.

The full Compose configuration starts PostgreSQL and the API. The API waits
until PostgreSQL is healthy, applies migrations, and then starts Uvicorn:

```bash
docker compose up --build -d
```

The API is available at:

- Swagger UI: <http://localhost:8000/docs>
- OpenAPI schema: <http://localhost:8000/openapi.json>

View API logs:

```bash
docker compose logs -f web
```

Stop the services:

```bash
docker compose down
```

The database is stored in the named `pgdata` volume. To stop the services and
remove the volume:

```bash
docker compose down -v
```

### Run locally

Start PostgreSQL in Docker using the development Compose file:

```bash
docker compose -f docker-compose-dev.yml up -d
```

Install Python dependencies and apply migrations:

```bash
poetry install
poetry run alembic upgrade head
```

Start the API with automatic reload:

```bash
poetry run uvicorn src.main:app --reload
```

For a regular start without reload:

```bash
poetry run uvicorn src.main:app
```

The local Uvicorn commands listen on `127.0.0.1:8000` by default.

## API

All resource endpoints use the `/api/v1` prefix. UUID path parameters must be
valid UUID values. Interactive request and response schemas are available in
Swagger UI at <http://localhost:8000/docs>.

### Service endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check that the service is alive |
| `GET` | `/readness` | Check database readiness |
| `GET` | `/version` | Return the application version |

Example responses:

```json
GET /health
{
  "status": "OK",
  "message": "Service is alive"
}
```

```json
GET /version
{
  "version": "0.4.0"
}
```

The readiness endpoint returns the status of the database connection:

```json
{
  "items": [
    {
      "service": "database",
      "is_alive": true,
      "msg": "Stable connection to database"
    }
  ]
}
```

### User endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/users/` | Create a user |
| `GET` | `/api/v1/users/` | List all users |
| `GET` | `/api/v1/users/{user_id}/` | Get a user with associated devices |
| `GET` | `/api/v1/users/{user_id}/stats/aggregated/` | Get aggregated statistics for all user devices |
| `GET` | `/api/v1/users/{user_id}/stats/devices/` | Get statistics for each user device |

Create a user:

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice"}'
```

The `name` field must contain between 2 and 100 characters. A successful
response has status `201 Created`.

Statistics endpoints accept optional `start_date` and `end_date` query
parameters:

```text
/api/v1/users/{user_id}/stats/aggregated/?start_date=2026-10-01T00:00:00&end_date=2026-10-31T23:59:59
```

### Device endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/devices/register_new_device/` | Register a device |
| `GET` | `/api/v1/devices/` | List all devices |
| `GET` | `/api/v1/devices/{device_id}/` | Get a device with associated users |
| `POST` | `/api/v1/devices/{device_id}/measurements/` | Add a measurement |
| `GET` | `/api/v1/devices/{device_id}/measurements/` | List device measurements |
| `GET` | `/api/v1/devices/{device_id}/stats/` | Get device statistics |
| `POST` | `/api/v1/devices/{device_id}/users/` | Associate a user with a device |
| `GET` | `/api/v1/devices/{device_id}/users/` | List users associated with a device |

Register a device:

```bash
curl -X POST http://localhost:8000/api/v1/devices/register_new_device/ \
  -H "Content-Type: application/json" \
  -d '{"serial_number":"DEV-100"}'
```

The serial number must contain between 3 and 30 characters and must be unique.

Add a measurement:

```bash
curl -X POST http://localhost:8000/api/v1/devices/{device_id}/measurements/ \
  -H "Content-Type: application/json" \
  -d '{"x":10.2,"y":20.1,"z":30.3}'
```

Measurement and device statistics endpoints also accept optional
`start_date` and `end_date` query parameters. Device statistics contain
`min`, `max`, `count`, `sum`, and `median` values for each measurement axis.

Associate an existing user with a device. The user ID is passed as a query
parameter:

```bash
curl -X POST "http://localhost:8000/api/v1/devices/{device_id}/users/?user_id={user_id}"
```

Common status codes include:

- `201 Created` for successfully created users, devices, measurements, and
  associations;
- `200 OK` for successful read operations;
- `400 Bad Request` for duplicate users, devices, or associations;
- `404 Not Found` when a requested user, device, or measurement does not exist;
- `422 Unprocessable Entity` when request validation fails.

## Database and seed data

Apply all migrations:

```bash
poetry run alembic upgrade head
```

The latest migration adds idempotent development data:

- users `dev_user` and `test_user`;
- devices `DEV-001`, `DEV-002`, and `TEST-001`;
- user-device associations;
- six measurements for device statistics examples.

Create a new migration after changing the database models:

```bash
poetry run alembic revision --autogenerate -m "describe the change"
```

Review autogenerated migrations before applying them. To roll back one
migration:

```bash
poetry run alembic downgrade -1
```

## Testing and code quality

Run the test suite:

```bash
poetry run pytest -v
```

Run the configured static checks:

```bash
poetry run mypy .
poetry run ruff check
poetry run flake8
```

Or use `pre-commit` that runs the configured code-quality checks automatically before a
commit. The `--all-files` option applies them to all files in the repository:

```bash
poetry run pre-commit run --all-files
```

The GitHub Actions workflow runs mypy, Ruff, Flake8, and pytest for pushes to
`main` and pull requests targeting `main`. Successful CI runs publish the
`src/` directory as the `application` artifact.

## Development

### Project structure

```text
gazprom-test-task/
├── .github/workflows/ci.yml       # CI checks and test workflow
├── src/
│   ├── core/                      # Settings, dependencies, logging, utilities
│   ├── database/                  # SQLAlchemy models, sessions, Alembic
│   ├── middleware/                # HTTP logging middleware
│   ├── routes/
│   │   ├── devices/               # Device and measurement API
│   │   ├── healthchecks/           # Health, readiness, and version API
│   │   └── users/                 # User and user statistics API
│   ├── app.py                     # FastAPI application factory
│   └── main.py                    # Application entry point
├── tests/                         # API tests
├── .env.example                   # Local environment template
├── alembic.ini                    # Alembic configuration
├── docker-compose-dev.yml         # PostgreSQL for local development
├── docker-compose.yml             # PostgreSQL and API services
├── Dockerfile                     # Production container image
├── poetry.lock                    # Locked dependencies
├── pyproject.toml                 # Project metadata and tooling
├── CHANGELOG.md                   # Release history
└── README.md                      # Project documentation
```
