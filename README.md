# Test Task API

## Table of Contents

- [What the application does](#what-the-application-does)
- [Assumptions](#assumptions)
- [Requirements](#requirements)
- [Environment variables](#environment-variables)
- [Run with Docker](#run-with-docker)
- [Run locally](#run-locally)
- [Health, version, and logs](#health-version-and-logs)
- [Tests](#tests)
- [Project Structure](#project-structure)

## What the application does

This is a FastAPI web application for managing users and devices. It provides
REST API endpoints for creating, reading, updating, and deleting users and
devices, as well as managing the relationships between them. The application
is intended for developers and operators who need a small service for
maintaining this data and checking the service and database status.

## Assumptions

1. A many-to-many relationship between `devices` and `users` is implemented
   because the original task did not specify the relationship type.

## Requirements

- Python 3.11 or later
- Poetry 2.x
- Docker and Docker Compose (for the containerized setup or the local database)

## Environment variables

The Compose files and the application read configuration from a `.env` file in
the project root. Do not commit real credentials to this file.

| Variable | Required | Description |
| --- | --- | --- |
| `POSTGRES_HOST` | Yes | PostgreSQL host name or address |
| `POSTGRES_USER` | Yes | PostgreSQL user |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `POSTGRES_DB` | Yes | PostgreSQL database name |
| `POSTGRES_PORT` | No | PostgreSQL port; defaults to `5432` |

For the Docker Compose stack, `POSTGRES_HOST` and `POSTGRES_PORT` for the web
service are set to `db` and `5432` automatically. The values in `.env` are
used for the PostgreSQL container credentials.

Copy the example file and adjust the values for your database:

```shell
cp .env.example .env
```

The resulting `.env` file should contain values like those in
[`.env.example`](.env.example). The `.env` file is ignored by Git and must not
contain credentials committed to the repository.

## Run with Docker

After cloning the repository, create the environment file and start the stack:

```shell
copy .env.example .env
docker compose up --build -d
```

The web application is available at
<http://localhost:8000/docs>. The container runs the database migrations before
starting the API and waits for PostgreSQL to become healthy first.

Inside the Compose network, the API connects to PostgreSQL using the `db`
service name and port `5432`. The same port is published on the host for
external database clients, so local tools can connect to `localhost:5432`.

View application logs with:

```shell
docker compose logs -f web
```

Stop the stack with `docker compose down`.

The database data is stored in the named `pgdata` volume. To remove the
database data as well, run:

```shell
docker compose down -v
```

## Run locally

Start only the development PostgreSQL database. The database is published on
`localhost:5432`:

```shell
docker compose -f docker-compose-dev.yml up -d
```

Create a Python environment and install dependencies:

```shell
poetry env use python3.11
poetry install
poetry run alembic upgrade head
```

The migrations populate a new database with example data: `dev_user` and
`test_user`, three associated devices, and six measurements for the device
statistics endpoints. The seed migration is idempotent and does not duplicate
these records when applied to an existing database.

Start the application in development mode with automatic reload:

```shell
poetry run uvicorn src.main:app --reload
```

Open the interactive API documentation at
<http://localhost:8000/docs>.

For normal operation, start the application without `--reload`:

```shell
poetry run uvicorn src.main:app
```

Alternatively, `python -m src.main` starts Uvicorn on `0.0.0.0:8081`.

## Health, version, and logs

With the application running, check its liveness and version:

```shell
curl http://localhost:8000/health
curl http://localhost:8000/version
```

`/health` returns the service liveness status. `/version` returns the
application version. The readiness endpoint is available at `/readness` and
checks database connectivity.

Local application logs are printed to the terminal as structured records. For
the Docker setup, use `docker compose logs -f web` (or
`docker logs -f fastapi_app`).

## Checks

The project currently has no automated test files or `pytest` dependency. The
same checks used by CI can be run locally after installing the development
dependencies:

```shell
poetry install
poetry run mypy .
poetry run ruff check
poetry run flake8
```

## Project Structure

```shell
test-task/
├── github/workflows
│   └── ci.yml
├── src/
│   ├── database
│   │   ├── alembic/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── middleware
│   │   ├── __init__.py
│   │   └── log_middleware.py
│   ├── routes
│   │   ├── devices
│   │   │   ├── __init__.py
│   │   │   ├── abstract_data_storage.py
│   │   │   ├── dao.py
│   │   │   ├── exceptions.py
│   │   │   ├── schemas.py
│   │   │   └── views.py
│   │   ├── users
│   │   │   ├── __init__.py
│   │   │   ├── abstract_data_storage.py
│   │   │   ├── dao.py
│   │   │   ├── exceptions.py
│   │   │   ├── schemas.py
│   │   │   └── views.py
│   │   └── healthchecks
│   │       ├── __init__.py
│   │       ├── schema.py
│   │       ├── spec.py
│   │       └── views.py
│   ├── core
│   │   ├── config_log.py
│   │   ├── dependencies.py
│   │   ├── settings.py
│   │   └── utils.py
│   ├── app.py
│   └── main.py
├── .dockerignore
├── .env                                    # Required for local configuration
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── CHANGELOG.md
├── docker-compose-dev.yml                  # PostgreSQL only for local development
├── docker-compose.yml                      # Full Docker Compose stack
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md
```
