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

This script will start the service with default configurations. You can override default values creating file `./src/config.yml` with the following values:

```
redis_host: localhost
redis_port: 6379
service_host: localhost
service_port: 5051
```

## Development and testing

A virtual env is needed for some of the development tasks

    ./run install_venv

start the service for testing (with a redis server included)

    ./run start:testing

Check service is working and get general info and supported languages

    curl --silent localhost:5051/info

Test Ocr is working

if language is not specified, english is the default

    curl -X POST -F 'file=@./src/test_files/sample-english.pdf' localhost:5051 --output english.pdf

specify a language for better ocr on supported languages, check `localhost:5051/info`

    curl -X POST -F 'language=fr' -F 'file=@./src/test_files/sample-french.pdf' localhost:5051 --output french.pdf

to list all available commands just run `./run`, some useful commands:

    ./run test
    ./run linter
    ./run check_format
    ./run formatter

## Contents

- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [How to use it asynchronously](#how-to-use-it-asynchronously)
- [HTTP server](#http-server)
- [Queue processor](#queue-processor)
- [Service configuration](#service-configuration)
- [Get service logs](#get-service-logs)
- [Troubleshooting](#troubleshooting)

## How to use it asynchronously

1. Send PDF to OCR

   curl -X POST -F 'file=@/PATH/TO/PDF/pdf_name.pdf' localhost:5051/upload/[namespace]

![Alt logo](readme_pictures/send_materials.png?raw=true "Send PDF to extract")

2. Add OCR task

To add an ocr task, a message should be sent to a queue.
params should include filename and optionally a language supported, check languages supported on `localhost:5051/info`

Python code:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='ocr_tasks', quiet=True)
    message_json = '{"tenant": "tenant_name", "task": "ocr", "params": {"filename": "pdf_file_name.pdf", "language": 'fr'}}'
    message = queue.sendMessage(message_json).exceptions(False).execute()

![Alt logo](readme_pictures/extraction.png?raw=true "Add extraction task")

3. Get OCRed pdf

When the ocr task is done, a message is placed in the results queue:

    queue = RedisSMQ(host=[redis host], port=[redis port], qname='ocr_results', quiet=True)
    results_message = queue.receiveMessage().exceptions(False).execute()

    # The message.message contains the following information:
    # {"tenant": "tenant_name",
    # "task": "pdf_name.pdf",
    # "success": true,
    # "error_message": "",
    # "file_url": "http://localhost:5051/processed_pdf/[namespace/tenant]/[pdf_name]"
    # }


    curl -X GET http://localhost:5051/processed_pdf/[namespace/tenant]/[pdf_name]

![Alt logo](readme_pictures/get_paragraphs.png?raw=true "Get PDF")

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
