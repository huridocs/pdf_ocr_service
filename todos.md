## TODOS

<!-- - all source code into src/ ? -->
<!-- - linter ! -->
<!-- - cleanup automaitcally for each tests -->

- do not use tenants, WTF ?
- change names of packages if pertinent
<!-- - combine docker-compose files (prod and testing) if possible -->
- divide dependencies into prod and dev requirements files
- rename venv to something meaningfull, ocr-pdf-service-venv ?
- why still docker_volumes has xml dir ?
- use config paths instead of repeating everywhere strings
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_results' already exists
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_tasks' already exists
