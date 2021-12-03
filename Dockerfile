FROM python:3.9-bullseye AS base

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y ocrmypdf

RUN mkdir /app
RUN mkdir /app/src
RUN mkdir /data
WORKDIR /app
COPY ./src ./src

FROM base AS api
WORKDIR /app
WORKDIR /app/src
COPY docker-compose.yml .
ENV FLASK_APP app.py
CMD gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5050

FROM base AS ocr
WORKDIR /app
COPY docker-compose.yml .
CMD python3 ./src/QueueProcessor.py
