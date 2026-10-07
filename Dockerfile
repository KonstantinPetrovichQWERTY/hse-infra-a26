FROM python:3.11.11-slim

ARG SRCDIR=src
ARG WORKDIR=/
RUN pip install poetry==2.1.1
COPY pyproject.toml \
     poetry.lock \
     README.md \
     .env \
     $WORKDIR
COPY $SRCDIR $WORKDIR/$SRCDIR/

WORKDIR $WORKDIR
RUN poetry config virtualenvs.create false
RUN poetry source add global https://pypi.org/simple

RUN poetry cache clear --all pypi

RUN poetry install --no-interaction --no-ansi -vvv --no-root

EXPOSE 8000
ENV PYTHONPATH=.

CMD sh -c "poetry run alembic -c src/database/alembic.ini upgrade head && poetry run uvicorn src.main:app"
