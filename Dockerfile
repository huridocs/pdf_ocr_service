FROM python:3.9-slim-bullseye AS base

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y ocrmypdf
RUN apt-get install -y tesseract-ocr-fra
RUN apt-get install -y tesseract-ocr-spa
RUN apt-get install -y tesseract-ocr-deu
RUN apt-get install -y tesseract-ocr-ara
RUN apt-get install -y tesseract-ocr-mya
RUN apt-get install -y tesseract-ocr-hin
RUN apt-get install -y tesseract-ocr-tam
RUN apt-get install -y tesseract-ocr-tha
RUN apt-get install -y tesseract-ocr-chi-sim

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add more languages as needed

RUN mkdir /app
RUN mkdir /app/src
RUN mkdir /data
WORKDIR /app
COPY ./src ./src

FROM base AS api
WORKDIR /app/src
COPY docker-compose.yml .
ENV FLASK_APP app.py
CMD gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5050 --timeout 300

FROM base AS ocr
WORKDIR /app/src
COPY docker-compose.yml .
CMD python3 QueueProcessor.py
