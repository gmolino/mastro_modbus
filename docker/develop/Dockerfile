FROM python:3.11

#Directorio en contenedor
WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - && \
   cd /usr/local/bin && \
   ln -s /etc/poetry/bin/poetry

COPY ./mastro_pull/ /app/
#COPY ./pyproject.toml ./poetry.lock* /app/

#RUN poetry install --no-root --only main
RUN poetry install --no-root
#RUN echo "alias mqttw='watch -n 5 rabbitmqctl list_queues name messages_ready messages_unacknowledged'" >> /etc/bash.bashrc

#CMD tail -f /dev/null
CMD poetry run python ./mastro_main.py
