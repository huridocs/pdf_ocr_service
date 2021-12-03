#!/bin/sh

python3 -m venv ocr-service-venv
source ocr-service-venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt