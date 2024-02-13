FROM python:3.10-alpine

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --system --deploy

ENV PIPENV_VIRTUALENV_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY . /app

CMD ["python", "main.py"]
