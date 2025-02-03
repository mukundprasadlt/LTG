FROM python:3.11-slim

RUN pip install poetry==1.6.1

RUN poetry config virtualenvs.create false

ENV ENVIRONMENT=dev
ENV PROVIDER=selfhosted
ENV KEYVAULT_ENDPOINT=nullendpoint

WORKDIR /code

COPY ./pyproject.toml ./README.md ./poetry.lock* ./

COPY ./package[s] ./packages

RUN poetry install  --no-interaction --no-ansi --no-root

COPY ./app ./app

RUN poetry install --no-interaction --no-ansi --only main

# CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8000
CMD exec streamlit run app/policy/ui.py

