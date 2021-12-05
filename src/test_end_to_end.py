import os
import json
import io
import shutil
import subprocess
import time
from unittest import TestCase
import pdfplumber
import requests
from rsmq import RedisSMQ

from ExtractionMessage import ExtractionMessage
from Params import Params
from Task import Task
from ServiceConfig import ServiceConfig

config = ServiceConfig()

class TestEndToEnd(TestCase):
    def setUp(self):
        shutil.rmtree(config.paths['source_pdfs'], ignore_errors=True)
        shutil.rmtree(config.paths['processed_pdfs'], ignore_errors=True)
        shutil.rmtree(config.paths['failed_pdfs'], ignore_errors=True)

    def setUpClass():
        subprocess.run('docker-compose --profile testing up -d --wait --build', shell=True)
        time.sleep(1)

    def tearDownClass():
        subprocess.run('docker-compose --profile testing down', shell=True)
        subprocess.run('docker-compose --profile testing rm', shell=True)

    def test_sync_ocr(self):
        pdf_file_name = 'source.pdf'
        service_url = 'http://localhost:5051'

        with open(f'{config.paths["app"]}/test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            response = requests.post(f"{service_url}", files=files)

        self.assertEqual(200, response.status_code)

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            first_page = pdf.pages[0]
            self.assertEqual('Test  text  OCR', first_page.extract_text())

    def test_async_ocr(self):
        root_path = '.'

        namespace = 'end_to_end_test'
        pdf_file_name = 'source.pdf'
        service_url = 'http://localhost:5051'

        with open(f'{config.paths["app"]}/test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{service_url}/upload/{namespace}", files=files)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="ocr_tasks")

        queue.sendMessage().message('{"message_to_avoid":"to_be_written_in_log_file"}').execute()

        task = Task(tenant=namespace, task='ocr', params=Params(filename=pdf_file_name))
        queue.sendMessage().message(str(task.json())).execute()

        extraction_message = self.get_redis_message()

        response = requests.get(extraction_message.file_url)
        self.assertEqual(200, response.status_code)

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            first_page = pdf.pages[0]
            self.assertEqual('Test  text  OCR', first_page.extract_text())

    def test_async_ocr_specific_language(self):
        root_path = '.'

        namespace = 'end_to_end'
        pdf_file_name = 'sample-french.pdf'
        service_url = 'http://localhost:5051'

        with open(f'{config.paths["app"]}/test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{service_url}/upload/{namespace}", files=files)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="ocr_tasks")

        queue.sendMessage().message('{"message_to_avoid":"to_be_written_in_log_file"}').execute()

        task = Task(tenant=namespace, task='ocr', params=Params(filename=pdf_file_name, language='fr'))
        queue.sendMessage().message(str(task.json())).execute()

        extraction_message = self.get_redis_message()

        response = requests.get(extraction_message.file_url)
        self.assertEqual(200, response.status_code)

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            first_page = pdf.pages[0]
            self.assertEqual("Où  puis-je  m'en  procurer", first_page.extract_text())

    def test_async_ocr_error_handling(self):
        namespace = 'end_to_end_test_error'
        pdf_file_name = 'README.md'
        service_url = 'http://localhost:5051'

        with open(f'{config.paths["app"]}/../README.md', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{service_url}/upload/{namespace}", files=files)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="ocr_tasks")
        task = Task(tenant=namespace, task='ocr', params=Params(filename=pdf_file_name))

        queue.sendMessage().message(task.json()).execute()

        extraction_message = self.get_redis_message()

        self.assertEqual(namespace, extraction_message.tenant)
        self.assertEqual('README.md', extraction_message.params.filename)
        self.assertEqual(False, extraction_message.success)
        self.assertTrue(os.path.exists(
            f'{config.paths["failed_pdfs"]}/{extraction_message.tenant}/{extraction_message.params.filename}'))

    @staticmethod
    def get_redis_message() -> ExtractionMessage:
        queue = RedisSMQ(host='127.0.0.1',
                         port='6479',
                         qname='ocr_results',
                         quiet=True)

        for i in range(50):
            time.sleep(0.5)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                queue.deleteMessage(id=message['id']).execute()
                return ExtractionMessage(**json.loads(message['message']))
