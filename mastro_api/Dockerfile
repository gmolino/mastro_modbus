FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app
COPY ../ /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create true

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

# COPY ./scripts/ /app/
# COPY ./alembic.ini /app/
# COPY ./prestart.sh /app/
# COPY ./tests-start.sh /app/
# CMD tail -f /dev/null
CMD poetry run uvicorn app.main:app --host=0.0.0.0 --port=5000 --reload

#poetry run alembic upgrade head
#alembic revision --autogenerate -m "new rev."