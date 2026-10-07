# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-10-07

### Added

- Add Pydantic schema documentation and field descriptions.
- Add pre-commit checks and update CI and Flake8 configuration.

### Changed

- Rework application settings configuration and environment variable handling.
- Simplify the application and Docker setup by removing Hypercorn configuration.
- Update development dependencies, migrations, Docker Compose files, and documentation.

### Removed

- Stop tracking the `.env` file and remove the obsolete `settings.toml` and Hypercorn configuration.

## [0.3.0] - 2025-04-10

### Added

- Add Docker support.
- Add User and Device endpoints.
- Add logging middleware.
- Set up logger.
- Add database session manager.
- Add alembic migrations.
- Set up a dev Docker Compose configuration to run PostgreSQL and Adminer.
- Add .env file.

## [0.2.0] - 2025-04-10

### Added

- Set up a dev Docker Compose configuration to run PostgreSQL and Adminer.
- Add .env file.

## [0.1.0] - 2025-04-10

### Added

- Init project.
- Add poetry.
- Add flake8 configuration.
- Add linter checks to GitHub Actions CI.
- Project structure.
