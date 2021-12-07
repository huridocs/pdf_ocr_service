# OCR PDFs

A Docker-powered service for OCRing PDFs

---

## Dependencies and requirements

- Redis server for managing queues
- Docker ([install](https://runnable.com/docker/getting-started/))
- Docker-compose ([install](https://docs.docker.com/compose/install/))
  - Note: On mac Docker-compose is installed with Docker

## Quick Start

Start the service:

    ./run start

This script will start the service with default configurations. You can override default values with file `./src/config.yml` (you may need to create the file) with the following values:

```
redis_host: localhost
redis_port: 6379
service_host: localhost
service_port: 5051
```

## Development and testing

A virtual env is needed for some of the development tasks

    ./run install_venv

Start the service for testing (with a redis server included)

    ./run start:testing

Check service is up and get general info on supported languages and other important information:

    curl localhost:5051/info

Test OCR is working (basic sync method)

curl -X POST -F 'file=@./src/test_files/sample-english.pdf' localhost:5051 --output english.pdf

If language is not specified, english will be used by default. In order to specify a language for better OCR results:

    curl -X POST -F 'language=fr' -F 'file=@./src/test_files/sample-french.pdf' localhost:5051 --output french.pdf

Remember you can check supported languages on `localhost:5051/info`

To list all available commands just run `./run`, some useful commands:

    ./run test
    ./run linter
    ./run check_format
    ./run formatter

## Contents

- [Asynchronous OCR](#asynchronous-ocr)
- [HTTP server](#http-server)
- [Retrieve OCRed PDF](#retrieve-ocred-pdf)
- [Queue processor](#queue-processor)
- [Service configuration](#service-configuration)
- [Get service logs](#get-service-logs)
- [Troubleshooting](#troubleshooting)

## Asynchronous OCR

1. Upload PDF file to the OCR service

   curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051/upload/[namespace]

![Alt logo](readme_pictures/send_materials.png?raw=true "Send PDF to extract")

2. Add OCR task to queue

To add an OCR task to queue, a message should be sent to a `ocr_tasks` Redis queue. Params should include filename and, optionally, a supported language.

Python code: TODO: check python code!!!

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='ocr_tasks', quiet=True)
    message_json = '{"tenant": "tenant_name", "task": "ocr", "params": {"filename": "pdf_file_name.pdf", "language": 'fr'}}'
    message = queue.sendMessage(message_json).exceptions(False).execute()

3. Retrieve OCRed PDF

Upon completion of the OCR process, a message is placed in the `ocr_results` Redis queue. This response is, for now, using specific Uwazi terminology. To check if the process for a specific file has been completed:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='ocr_results', quiet=True)
    results_message = queue.receiveMessage().exceptions(False).execute()

    # The message.message contains the following information:
    # {
    #   "tenant": "namespace",
    #   "task": "pdf_name.pdf",
    #   "success": true,
    #   "error_message": "",
    #   "file_url": "http://localhost:5051/processed_pdf/[namespace]/[pdf_name]"
    #   }


    curl -X GET http://localhost:5051/processed_pdf/[namespace]/[pdf_name]

## HTTP server

The container `HTTP server` is coded using Python 3.9 and uses the [FastApi](https://fastapi.tiangolo.com/) web framework.

If the service is running, the end point definitions can be founded in the following url:

    http://localhost:5051/docs

The end points code can be founded inside the file `app.py`.

The errors are reported to the file `docker_volume/service.log`, if the configuration is not changed (see [Get service logs](#get-service-logs))

## Queue processor

The container `Queue processor` is coded using Python 3.9, and it is on charge of the communication with redis.

The code can be founded in the file `QueueProcessor.py` and it uses the library `RedisSMQ` to interact with the
redis queues.

## Troubleshooting

In MacOS, it can be used the following config.yml in order to access to the redis in localhost:

    redis_host: host.docker.internal
    redis_port: 6379
    service_host: localhost
    service_port: 5051

### Issue: Error downloading pip wheel

Solution: Change RAM memory used by the docker containers to 3Gb or 4Gb
