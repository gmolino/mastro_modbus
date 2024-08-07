FROM python:3.11

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - && \
   cd /usr/local/bin && \
   ln -s /etc/poetry/bin/poetry

COPY ./mastro_consumer/ /app/
RUN poetry install --no-root --only main

#CMD tail -f /dev/null
CMD poetry run python mqtt_consume.py