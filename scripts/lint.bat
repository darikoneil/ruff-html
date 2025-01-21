@echo off

:: move to project root
cd ..

:: formatting imports (paths because the config is broken & don't care to make it work)
isort ./%PROJECT_NAME% ./tests

:: formatting code (paths because the config is broken & don't care to make it work)
black ./%PROJECT_NAME% ./tests

:: linting (putting paths here too because autism)
flake8 ./%PROJECT_NAME%
