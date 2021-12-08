## TODOS

<!-- - all source code into src/ ? -->
<!-- - linter ! -->
<!-- - cleanup automaitcally for each tests -->
<!-- - do not use tenants, WTF ? -->
<!-- - review test files: do we want to include the "processed.pdf" in the commit? -->
<!-- - combine docker-compose files (prod and testing) if possible -->
<!-- - change names of packages if pertinent -->
<!-- - error handling -->
<!-- - check passing parameters for OCRing, specicially language -->
<!-- - rename venv to something meaningfull, ocr-pdf-service-venv ? -->
<!-- - use config paths instead of repeating everywhere strings -->
<!-- - test with language for sync endpoint !! -->
<!-- - autoformatter -->
<!-- - info endpoint respond with languages available -->
<!-- - update README!!!! -->
<!-- - why still docker_volumes has xml dir ? -->
<!-- - test with a wider variety of PDFs -->
<!-- - review which requirements are really required -->
<!-- - be able to use external Redis -->

- `upload` route is returning `task registered` which is NOT true, should be something like `upload accepted`
- cleanup (delete) downloaded PDF files?
- unify logs into service.log, rename to ocr_pdf.log???
- README code does not include import RedisSMQ
- setup production environment with auto restart ?
- config logs path to be able to use /var/logs on production ?
- change the PORT number default in order to be able to be installed along-side our other services in the same machine. Should we have a pattern for future services?
- create `config.yml` with default values instead of explanation of creating the file
- make sure tests use config for testing redis container
- setup github CI with lint, formatting, tests ...
- make sure logs work
- make sure works on mac
- decide which languages to support
- divide dependencies into prod and dev requirements files
- setup_venv needs to stop on error to avoid insalling local packages
- allow upping the service without redis if you only want to use the sync method
- Check this warnings on docker-compose up:
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_results' already exists
  ocr_1 | QueueAlreadyExists: Exception while processing CreateQueueCommand: Queue 'ocr_tasks' already exists
