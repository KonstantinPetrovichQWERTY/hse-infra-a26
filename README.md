# severstal-test

## Assumptions

1. I decided to implement a many-to-many relationship between the `devices` and `users` due to the omission in the task.

## How to run

1. Use Docker after `git clone ...`.

```shell
docker compose up -d
```

Web application is running on <http://0.0.0.0:8081/docs> / <http://localhost:8081/docs>

Adminer for easier database managment is running on <http://localhost:8080/> (system = `PostgreSQL`, Server = `db`, username = `postgres`, password = `password`, database = `gazprom_db`)

1. To run locally you need to set up database:

```shell
docker-compose -f docker-compose-dev.yml up -d
```

```shell
pip install poetry
poetry install
poetry alembic upgrade head
poetry run uvicorn main:app --reload
```

WARNING: Up venv python 3.11 and use first method to run :)

## Project Structure

```shell
severstal-test/
├── github/workflows
│   └── ci.yml
├── src/
│   ├── database
│   │   ├── alembic/
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
│   │   ├── config_log.py
│   │   ├── settings.py
│   │   ├── utils.py
│   │   └── version.py
├── .dockerignore
├── .env                                    # Required for local configuration
├── .gitignore
├── alembic.ini
├── CHANGELOG.md
├── docker-compose-dev.yml                  # Configuration file for dev docker compose (no web) 
├── docker-compose.yml                      # Configuration file for "production" docker compose
├── Dockerfile
├── main.py
├── poetry.lock
├── pyproject.toml
├── README.md
```
