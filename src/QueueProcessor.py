import os
from pydantic import ValidationError
from queue_processor.QueueProcessor import QueueProcessor
from sentry_sdk.integrations.redis import RedisIntegration
import sentry_sdk

from ServiceConfig import ServiceConfig, QUEUES_NAMES
from ExtractionMessage import ExtractionMessage

from Task import Task
from ocr_pdf import ocr_pdf


def process(message):
    service_config = ServiceConfig()
    logger = service_config.get_logger("redis_tasks")
    try:
        task = Task(**message)
    except ValidationError:
        logger.error(f"Not a valid message: {message}")
        return None

    logger.info(f"Valid message: {message}")

    try:
        processed_pdf_filepath = ocr_pdf(
            task.params.filename, task.tenant, task.params.language
        )

        if not processed_pdf_filepath:
            extraction_message = ExtractionMessage(
                tenant=task.tenant,
                task=task.task,
                params=task.params,
                success=False,
                error_message="Error during pdf ocr",
            )

            logger.error(extraction_message.json())
            return extraction_message.dict()

        processed_pdf_url = f"{service_config.service_url}/processed_pdf/{task.tenant}/{task.params.filename}"
        extraction_message = ExtractionMessage(
            tenant=task.tenant,
            task=task.task,
            params=task.params,
            success=True,
            file_url=processed_pdf_url,
        )

        logger.info(extraction_message.json())
        return extraction_message.dict()
    except Exception:
        logger.error("error", exc_info=1)
        return None


if __name__ == "__main__":
    try:
        sentry_sdk.init(
            os.environ.get("SENTRY_OCR_DSN"),
            traces_sample_rate=0.1,
            environment=os.environ.get("ENVIRONMENT", "development"),
            integrations=[RedisIntegration()],
        )
    except Exception:
        pass

    service_config = ServiceConfig()
    logger = service_config.get_logger("redis_tasks")
    queue_processor = QueueProcessor(
        service_config.redis_host,
        service_config.redis_port,
        service_config.queues_names,
        logger,
    )
    queue_processor.start(process)
