FROM python:3.10-alpine AS builder

WORKDIR /app

RUN apk update && apk add --no-cache build-base && pip install pipenv

ENV PIPENV_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY Pipfile Pipfile.lock /app/

RUN pipenv requirements --dev > requirements.txt && \
    pip install --no-cache-dir --no-deps -r requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

COPY . /app

CMD ["python", "src/main.py"]
