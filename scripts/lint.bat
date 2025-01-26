@echo off

echo [0;33m "Formatting & Linting --> ruff-html" [0m

:: move to project root
cd ..

echo [0;33m "Formatting (RUFF)..." [0m
:: run ruff formatter
ruff format

echo [0;33m "Linting (RUFF)..." [0m
:: run ruff linter
ruff check ./ruff_html ./tests -o .ruff.json

echo [0;33m "Linting (FLAKE8 PLUGINS)..." [0m
:: run flake8 first to check dunder all and class attributes order
flake8 ./ruff_html ./tests

echo [0;33m "Finished Formatting & Linting --> ruff-html" [0m
