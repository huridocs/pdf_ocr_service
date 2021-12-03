## TODOS

<!-- - all source code into src/ ? -->
<!-- - linter ! -->
<!-- - cleanup automaitcally for each tests -->
<!-- - do not use tenants, WTF ? -->
<!-- - review test files: do we want to include the "processed.pdf" in the commit? -->
<!-- - combine docker-compose files (prod and testing) if possible -->
<!-- - change names of packages if pertinent -->

- update README!!!!
- test with a wider variety of PDFs
- error handling
- check passing parameters for OCRing, specicially language
- autoformatter
- divide dependencies into prod and dev requirements files
- review which requirements are really required
- rename venv to something meaningfull, ocr-pdf-service-venv ?
- why still docker_volumes has xml dir ?
- use config paths instead of repeating everywhere strings
- setup_venv needs to stop on error to avoid insalling local packages
- Check this warnings on docker-compose up:
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_results' already exists
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_tasks' already exists
