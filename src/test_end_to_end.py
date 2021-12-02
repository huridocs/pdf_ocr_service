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


class TestEndToEnd(TestCase):
    def setUp(self):
        shutil.rmtree('../data/source_pdfs', ignore_errors=True)
        shutil.rmtree('../data/processed_pdfs', ignore_errors=True)
        shutil.rmtree('../data/failed_pdfs', ignore_errors=True)

    def setUpClass():
        subprocess.run('docker-compose -f ../docker-compose.yml -f ../docker-compose-dev.yml build --force-rm', shell=True)
        subprocess.run('docker-compose -f ../docker-compose.yml -f ../docker-compose-dev.yml up -d', shell=True)
        time.sleep(5)

    def tearDownClass():
        subprocess.run('docker-compose -f ../docker-compose.yml -f ../docker-compose-dev.yml down', shell=True)
        subprocess.run('docker-compose -f ../docker-compose.yml -f ../docker-compose-dev.yml rm -f', shell=True)

    def test_sync_ocr(self):
        root_path = '.'
        pdf_file_name = 'source.pdf'
        service_url = 'http://localhost:5051'

        with open(f'{root_path}/test_files/{pdf_file_name}', 'rb') as stream:
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

        with open(f'{root_path}/test_files/{pdf_file_name}', 'rb') as stream:
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

        # self.assertFalse(os.path.exists(f'{data_path}/processed_pdfs/{namespace}/{pdf_file_name}'))

        # shutil.rmtree(f'{data_path}/xml/{tenant}', ignore_errors=True)

        # tenant = 'end_to_end_test_error'
        # pdf_file_name = 'README.md'

        # with open(f'{root_path}/README.md', 'rb') as stream:
        #     files = {'file': stream}
        #     requests.post(f"{service_url}/async_extraction/{tenant}", files=files)

        # task = Task(tenant=tenant, task='segmentation', params=Params(filename=pdf_file_name))

        # queue.sendMessage().message(task.json()).execute()

        # extraction_message = self.get_redis_message()

        # self.assertEqual(tenant, extraction_message.tenant)
        # self.assertEqual('README.md', extraction_message.params.filename)
        # self.assertEqual(False, extraction_message.success)
        # self.assertTrue(os.path.exists(
        #     f'{data_path}/failed_pdf/{extraction_message.tenant}/{extraction_message.params.filename}'))

        # shutil.rmtree(f'{data_path}/failed_pdf/{tenant}', ignore_errors=True)

    @staticmethod
    def get_redis_message() -> ExtractionMessage:
        queue = RedisSMQ(host='127.0.0.1',
                         port='6479',
                         qname='ocr_results',
                         quiet=True)

        for i in range(10):
            time.sleep(2)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                queue.deleteMessage(id=message['id']).execute()
                return ExtractionMessage(**json.loads(message['message']))
