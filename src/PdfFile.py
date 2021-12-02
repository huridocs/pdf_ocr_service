import os
import pathlib
from pathlib import Path


class PdfFile:
    def __init__(self, tenant: str):
        path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.root_folder = path.parent.absolute()
        self.tenant = tenant

    def save(self, pdf_file_name: str, file: bytes):
        if not os.path.exists(f'{self.root_folder}/../data/source_pdfs'):
            os.mkdir(f'{self.root_folder}/../data/source_pdfs')

        if not os.path.exists(f'{self.root_folder}/../data/source_pdfs/{self.tenant}'):
            os.mkdir(f'{self.root_folder}/../data/source_pdfs/{self.tenant}')

        path = f'{self.root_folder}/../data/source_pdfs/{self.tenant}/{pdf_file_name}'

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
