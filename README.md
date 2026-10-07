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

The application reads configuration from a `.env` file in the project root.
Do not commit real credentials to this file.

| Variable | Required | Description |
| --- | --- | --- |
| `POSTGRES_HOST` | Yes | PostgreSQL host name or address |
| `POSTGRES_USER` | Yes | PostgreSQL user |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `POSTGRES_DB` | Yes | PostgreSQL database name |
| `POSTGRES_PORT` | No | PostgreSQL port; defaults to `5432` |

For local development, copy the example file and adjust the values for your
database:

```shell
cp .env.example .env
```

The resulting `.env` file should contain values like those in
[`.env.example`](.env.example). The `.env` file is ignored by Git and must not
contain credentials that are committed to the repository.

## Run with Docker

After cloning the repository, start the full stack:

```shell
docker compose up -d
```

The web application is available at
<http://localhost:8000/docs>. The container runs the database migrations before
starting the API.

Inside the Compose network, the API connects to PostgreSQL using the `db`
service name and port `5432`; the host-side port `5433` is only for external
database clients.

Adminer is available at <http://localhost:8080/> for database management. Use
system `PostgreSQL`, server `db`, and the credentials configured in the
environment.

View application logs with:

```shell
docker compose logs -f web
```

Stop the stack with `docker compose down`.

## Run locally

Start only the development PostgreSQL database:

```shell
docker compose -f docker-compose-dev.yml up -d
```

Create a Python environment and install dependencies:

```shell
poetry env use python3.11
poetry install
poetry run alembic -c src/database/alembic.ini upgrade head
```

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

Alternatively, `python -m src.main` starts Uvicorn on `127.0.0.1:8000`.

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

## Tests

Install the development dependencies with `poetry install`, then run:

```shell
poetry run pytest
```

There are currently no test files in the repository, so this command will
report that no tests were collected once `pytest` is available. `pytest` is not
currently declared as a development dependency. The CI workflow currently runs
the linters and type checker; the pytest step is prepared but disabled until
tests are added.

## Project Structure

```shell
test-task/
├── github/workflows
│   └── ci.yml
├── src/
│   ├── database
│   │   ├── alembic/
│   │   ├── alembic.ini
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── middlware
│   │   ├── __init__.py
│   │   └── log_middlware.py
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
│   │   ├── healthchecks
│   │   │   ├── __init__.py
│   │   │   ├── schema.py
│   │   │   ├── spec.py
│   │   │   └── views.py
│   │   ├── __init__.py
│   │   ├── app.py
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
├── CHANGELOG.md
├── docker-compose-dev.yml                  # Configuration file for dev docker compose (no web)
├── docker-compose.yml                      # Configuration file for "production" docker compose
├── Dockerfile
├── poetry.lock
├── pyproject.toml
├── README.md
```
