import os
import shutil
import pathlib
import subprocess

from ServiceConfig import ServiceConfig
from languages import iso_to_tesseract

config = ServiceConfig()

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()
DATA_PATH = f"{THIS_SCRIPT_PATH}/../data"


def get_paths(namespace: str, pdf_file_name: str):
    file_name = "".join(pdf_file_name.split(".")[:-1])
    source_pdf_filepath = f'{config.paths["source_pdfs"]}/{namespace}/{pdf_file_name}'
    processed_pdf_filepath = (
        f'{config.paths["processed_pdfs"]}/{namespace}/{file_name}.pdf'
    )
    failed_pdf_filepath = f'{config.paths["failed_pdfs"]}/{namespace}/{pdf_file_name}'
    return source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath


def ocr_pdf(filename, namespace, language="en"):
    source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath = get_paths(
        namespace, filename
    )
    os.makedirs("/".join(processed_pdf_filepath.split("/")[:-1]), exist_ok=True)
    result = subprocess.run(
        [
            "ocrmypdf",
            "-l",
            iso_to_tesseract[language],
            source_pdf_filepath,
            processed_pdf_filepath,
        ]
    )

    if result.returncode == 0:
        return processed_pdf_filepath

    if not os.path.exists(f'{config.paths["failed_pdfs"]}/{namespace}'):
        os.makedirs(f'{config.paths["failed_pdfs"]}/{namespace}', exist_ok=True)
    shutil.move(source_pdf_filepath, failed_pdf_filepath)
    return False
