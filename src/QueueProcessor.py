import os
from time import sleep

import redis
from pydantic import ValidationError
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ
from sentry_sdk.integrations.redis import RedisIntegration
import sentry_sdk

from ServiceConfig import ServiceConfig
from ExtractionMessage import ExtractionMessage

from Task import Task
from ocr_pdf import ocr_pdf


class QueueProcessor:
    def __init__(self):
        self.config = ServiceConfig()
        self.logger = self.config.get_logger("redis_tasks")

        self.results_queue = RedisSMQ(
            host=self.config.redis_host,
            port=self.config.redis_port,
            qname=self.config.results_queue_name,
        )

    def process(self, id, message, rc, ts):
        try:
            task = Task(**message)
        except ValidationError:
            self.logger.error(f"Not a valid message: {message}")
            return True

        self.logger.info(f"Valid message: {message}")

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

                self.results_queue.sendMessage().message(
                    extraction_message.dict()
                ).execute()
                self.logger.error(extraction_message.json())
                return True

            processed_pdf_url = f"{self.config.service_url}/processed_pdf/{task.tenant}/{task.params.filename}"
            extraction_message = ExtractionMessage(
                tenant=task.tenant,
                task=task.task,
                params=task.params,
                success=True,
                file_url=processed_pdf_url,
            )

            self.logger.info(extraction_message.json())
            self.results_queue.sendMessage(delay=3).message(
                extraction_message.dict()
            ).execute()
            return True
        except Exception:
            self.logger.error("error", exc_info=1)
            return True

    def subscribe_to_extractions_tasks_queue(self):
        while True:
            try:
                self.results_queue.createQueue().vt(120).exceptions(False).execute()
                extractions_tasks_queue = RedisSMQ(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    qname=self.config.tasks_queue_name,
                )

                extractions_tasks_queue.createQueue().vt(120).exceptions(
                    False
                ).execute()

                self.logger.info(
                    f"Connecting to redis: {self.config.redis_host}:{self.config.redis_port}"
                )

                redis_smq_consumer = RedisSMQConsumer(
                    qname=self.config.tasks_queue_name,
                    processor=self.process,
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                )
                redis_smq_consumer.run()
            except redis.exceptions.ConnectionError:
                self.logger.error(
                    f"Error connecting to redis: {self.config.redis_host}:{self.config.redis_port}"
                )
                sleep(20)


if __name__ == "__main__":
    try:
        sentry_sdk.init(
<<<<<<< HEAD
            os.environ.get("SENTRY_OCR_DSN"),
||||||| parent of 475a5e3 (Configure Sentry with env variables)
            "https://31f2bc6fdc8a4f36bb4e464ec1237765@o1134623.ingest.sentry.io/6212895",
=======
            os.environ.get('SENTRY_OCR_DSN'),
>>>>>>> 475a5e3 (Configure Sentry with env variables)
            traces_sample_rate=0.1,
            environment=os.environ.get("ENVIRONMENT", "development"),
            integrations=[RedisIntegration()],
        )
    except Exception:
        pass

    redis_tasks_processor = QueueProcessor()
    redis_tasks_processor.subscribe_to_extractions_tasks_queue()
