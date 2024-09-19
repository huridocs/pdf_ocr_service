import os
import logging
import graypy
import yaml

from pathlib import Path
from typing import Dict


OPTIONS = ["redis_host", "redis_port", "service_host", "service_port"]


APP_PATH = Path(__file__).parent.absolute()
DATA_PATH = f"{APP_PATH}/../data"
PDF_SOURCES_PATH = f"{DATA_PATH}/source_pdfs"
PDF_PROCESSED_PATH = f"{DATA_PATH}/processed_pdfs"
PDF_FAILED = f"{DATA_PATH}/failed_pdfs"

QUEUES_NAMES = os.environ.get("QUEUES_NAMES", "ocr")


class ServiceConfig:
    def __init__(self):
        self.paths: Dict[str, str] = dict(
            {
                "app": APP_PATH,
                "data": DATA_PATH,
                "source_pdfs": PDF_SOURCES_PATH,
                "processed_pdfs": PDF_PROCESSED_PATH,
                "failed_pdfs": PDF_FAILED,
            }
        )

        self.config_path = "config.yml"
        self.config_from_yml: Dict[str, any] = dict()
        self.read_configuration_from_yml()

        self.redis_host = self.get_parameter_from_yml("redis_host", "localhost")
        self.redis_port = self.get_parameter_from_yml("redis_port", 6379)

        default_service_port = 5050

        self.service_host = self.get_parameter_from_yml("service_host", "127.0.0.1")
        self.service_port = self.get_parameter_from_yml(
            "service_port", default_service_port
        )
        self.service_url = f"http://{self.service_host}:{self.service_port}"

    def get_parameter_from_yml(self, parameter_name: str, default: any):
        if parameter_name in self.config_from_yml:
            return self.config_from_yml[parameter_name]

        return default

    def read_configuration_from_yml(self):
        if not os.path.exists(self.config_path):
            return dict()

        with open(self.config_path, "r") as f:
            config_from_yml = yaml.safe_load(f)
            if config_from_yml:
                self.config_from_yml = config_from_yml

        return dict()

    def get_logger(self, logger_name):
        logger = logging.getLogger("graylog")
        logger.setLevel(logging.INFO)

        if (
            "graylog_ip" not in self.config_from_yml
            or not self.config_from_yml["graylog_ip"]
        ):
            logger.addHandler(
                logging.FileHandler(f'{self.paths["data"]}/{logger_name}.log')
            )
            return logger

        handler = graypy.GELFUDPHandler(
            self.config_from_yml["graylog_ip"], 12201, localname="pdf_ocr_service"
        )
        logger.addHandler(handler)
        return logger
