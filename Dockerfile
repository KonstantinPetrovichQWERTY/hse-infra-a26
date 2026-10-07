FROM python:3.11.11-slim

ARG SRCDIR=src
ARG WORKDIR=/
RUN pip install poetry==2.1.1
COPY pyproject.toml \
     poetry.lock \
     settings.toml \
     main.py \
     alembic.ini \
     README.md \
     .env \
     $WORKDIR
COPY $SRCDIR $WORKDIR/$SRCDIR/

WORKDIR $WORKDIR
RUN poetry config virtualenvs.create false
RUN poetry source add global https://pypi.org/simple

RUN poetry cache clear --all pypi

RUN poetry install --no-interaction --no-ansi -vvv --no-root

EXPOSE 8080
ENV PYTHONPATH=.

CMD sh -c "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8081"
