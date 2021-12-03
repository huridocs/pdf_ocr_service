import os
import pathlib
import subprocess

from ServiceConfig import ServiceConfig

config = ServiceConfig()

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()
DATA_PATH = f'{THIS_SCRIPT_PATH}/../data'


def get_paths(namespace: str, pdf_file_name: str):
    file_name = ''.join(pdf_file_name.split('.')[:-1])
    source_pdf_filepath = f'{config.paths["source_pdfs"]}/{namespace}/{pdf_file_name}'
    processed_pdf_filepath = f'{config.paths["processed_pdfs"]}/{namespace}/{file_name}.pdf'
    # failed_pdf_filepath = f'{config.paths["failed_pdfs"]}/{namespace}/{pdf_file_name}'
    # return source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath
    return source_pdf_filepath, processed_pdf_filepath


def ocr_pdf(filename, namespace):
    source_pdf_filepath, processed_pdf_filepath = get_paths(namespace, filename)
    os.makedirs('/'.join(processed_pdf_filepath.split('/')[:-1]), exist_ok=True)
    subprocess.run(['ocrmypdf', source_pdf_filepath, processed_pdf_filepath])
    return processed_pdf_filepath
