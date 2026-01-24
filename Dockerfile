FROM python:3.13-slim
LABEL authors="mks_min"

RUN pip install poetry && poetry config virtualenvs.create false

WORKDIR /backend

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --only main

COPY ./app ./app

CMD ["poetry", "run", "python", "app/run.py"]