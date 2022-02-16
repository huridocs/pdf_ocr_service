import os
import sys

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from typing import Optional
from fastapi.responses import FileResponse, JSONResponse
import subprocess

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import sentry_sdk

from ServiceConfig import ServiceConfig
from PdfFile import PdfFile
from ocr_pdf import ocr_pdf
from fastapi.encoders import jsonable_encoder
from languages import supported_languages

config = ServiceConfig()
logger = config.get_logger("service")

app = FastAPI()

logger.info("Ocr PDF service has started")

try:
    sentry_sdk.init(
        os.environ.get("SENTRY_OCR_DSN"),
        traces_sample_rate=0.1,
        environment=os.environ.get("ENVIRONMENT", "development"),
    )
    app.add_middleware(SentryAsgiMiddleware)
except Exception:
    pass



try:
    sentry_sdk.init(
        os.environ.get('SENTRY_OCR_DSN'),
        traces_sample_rate=0.1,
)
    app.add_middleware(SentryAsgiMiddleware)
except Exception:
    pass

@app.get("/info")
async def info():
    logger.info("Ocr PDF info endpoint")

    content = jsonable_encoder(
        {
            "sys": sys.version,
            "tesseract_version": subprocess.run(
                "tesseract --version", shell=True, text=True, capture_output=True
            ).stdout,
            "ocrmypdf_version": subprocess.run(
                "ocrmypdf --version", shell=True, text=True, capture_output=True
            ).stdout,
            "supported_languages": supported_languages(),
        }
    )
    return JSONResponse(content=content)


@app.get("/error")
async def error():
    logger.error("This is a test error from the error endpoint")
    raise HTTPException(
        status_code=500, detail="This is a test error from the error endpoint"
    )


@app.post("/")
async def ocr_pdf_sync(
    file: UploadFile = File(...), language: Optional[str] = Form("en")
):
    filename = "No file name"
    try:
        namespace = "sync_pdfs"
        filename = file.filename
        pdf_file = PdfFile(namespace)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        processed_pdf_filepath = ocr_pdf(filename, namespace, language)
        return FileResponse(path=processed_pdf_filepath, media_type="application/pdf")
    except Exception:
        message = f"Error processing {filename}"
        logger.error(message, exc_info=1)
        raise HTTPException(status_code=422, detail=message)


@app.post("/upload/{namespace}")
async def upload_pdf(namespace, file: UploadFile = File(...)):
    filename = "No file name"
    try:
        filename = file.filename
        pdf_file = PdfFile(namespace)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        return "File uploaded"
    except Exception:
        message = f"Error uploading pdf {filename}"
        logger.error(message, exc_info=1)
        raise HTTPException(status_code=422, detail=message)


@app.get("/processed_pdf/{namespace}/{pdf_file_name}", response_class=FileResponse)
async def processed_pdf(namespace: str, pdf_file_name: str):
    try:
        return FileResponse(
            path=f'{config.paths["processed_pdfs"]}/{namespace}/{pdf_file_name}',
            media_type="application/pdf",
            filename=pdf_file_name,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No processed file found")
    except Exception:
        logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422)
