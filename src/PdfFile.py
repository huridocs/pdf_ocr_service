import os
import pathlib
from pathlib import Path
from ServiceConfig import ServiceConfig

config = ServiceConfig()


class PdfFile:
    def __init__(self, namespace: str):
        path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.root_folder = path.parent.absolute()
        self.namespace = namespace

    def save(self, pdf_file_name: str, file: bytes):
        if not os.path.exists(config.paths["source_pdfs"]):
            os.mkdir(config.paths["source_pdfs"])

        if not os.path.exists(f'{config.paths["source_pdfs"]}/{self.namespace}'):
            os.mkdir(f'{config.paths["source_pdfs"]}/{self.namespace}')

        path = f'{config.paths["source_pdfs"]}/{self.namespace}/{pdf_file_name}'

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
