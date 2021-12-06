import sys
import logging

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from typing import Optional
from fastapi.responses import FileResponse, JSONResponse
import subprocess

from ServiceConfig import ServiceConfig
from PdfFile import PdfFile
from ocr_pdf import ocr_pdf
from fastapi.encoders import jsonable_encoder
from languages import supported_languages

config = ServiceConfig()
logger = config.get_logger('service')

app = FastAPI()

logger.info('Ocr PDF service has started')


@app.get('/info')
async def info():
    logger.info('Ocr PDF info endpoint')

    content = jsonable_encoder({
            "sys": sys.version,
            "tesseract_version": subprocess.run("tesseract --version", shell=True, text=True, capture_output=True).stdout,
            "ocrmypdf_version": subprocess.run("ocrmypdf --version", shell=True, text=True, capture_output=True).stdout,
            "supported_languages": supported_languages()
            })
    return JSONResponse(content=content)


@app.post('/')
async def ocr_pdf_sync(file: UploadFile = File(...), language: Optional[str] = Form('en')):
    filename = 'No file name'
    try:
        namespace = 'sync_pdfs'
        filename = file.filename
        pdf_file = PdfFile(namespace)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        processed_pdf_filepath = ocr_pdf(filename, namespace, language)
        return FileResponse(path=processed_pdf_filepath, media_type='application/pdf')
    except Exception:
        message = f'Error processing {filename}'
        logger.error(message, exc_info=1)
        raise HTTPException(status_code=422, detail=message)


@app.post('/upload/{namespace}')
async def upload_pdf(namespace, file: UploadFile = File(...)):
    filename = 'No file name'
    try:
        filename = file.filename
        pdf_file = PdfFile(namespace)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        return 'task registered'
    except Exception:
        message = f'Error uploading pdf {filename}'
        logger.error(message, exc_info=1)
        raise HTTPException(status_code=422, detail=message)


@app.get('/processed_pdf/{namespace}/{pdf_file_name}', response_class=FileResponse)
async def processed_pdf(namespace: str, pdf_file_name: str):
    try:
        return FileResponse(
            path=f'{config.paths["processed_pdfs"]}/{namespace}/{pdf_file_name}',
            media_type='application/pdf',
            filename=pdf_file_name
            )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No processed file found')
    except Exception:
        logger.error('Error', exc_info=1)
        raise HTTPException(status_code=422)
