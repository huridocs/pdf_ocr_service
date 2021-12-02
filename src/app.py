import sys

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse

from ServiceConfig import ServiceConfig
from PdfFile import PdfFile
from ocr_pdf import ocr_pdf

config = ServiceConfig()
logger = config.get_logger('service')

app = FastAPI()

logger.info('Ocr PDF service has started')


@app.get('/info')
async def info():
    logger.info('Ocr PDF info endpoint')
    return sys.version


# @app.get('/error')
# async def error():
#     logger.error("This is a test error from the error endpoint")
#     raise HTTPException(status_code=500, detail='This is a test error from the error endpoint')


@app.post('/')
async def ocr_pdf_sync(file: UploadFile = File(...)):
    filename = 'No file name'
    try:
        namespace = 'sync_pdfs'
        filename = file.filename
        pdf_file = PdfFile(namespace)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        processed_pdf_filepath = ocr_pdf(filename, namespace)
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
        return FileResponse(path=f'../data/processed_pdfs/{namespace}/{pdf_file_name}', media_type='application/pdf', filename=pdf_file_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No processed file found')
    except Exception:
        logger.error('Error', exc_info=1)
        raise HTTPException(status_code=422)