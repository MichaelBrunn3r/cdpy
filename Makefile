
PYTHON = poetry run py
PROTOCOL_VERSION = 1.3
GENERATED_OUTDIR = ./cdpy/cdp
GET_POETRY_URI = https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py

# Install poetry on osx/linux
.PHONY: install-poetry
install-poetry:
	curl -sSL $(GET_POETRY_URI) | python -

# Install poetry on windows
.PHONY: install-poetry-win
install-poetry-win:
	(Invoke-WebRequest -Uri $(GET_POETRY_URI) -UseBasicParsing).Content | python -

# Setup the project
.PHONY: setup
setup:
	poetry lock -n
	poetry install -n
	poetry run pre-commit install

# Generate chrome devtools protocol wrapper
.PHONY: generate-cdp
generate-cdp:
	$(PYTHON) .\generator\gen.py generate $(PROTOCOL_VERSION) $(GENERATED_OUTDIR)

.PHONY: test
test:
	$(PYTHON) -m pytest

.PHONY: coverage
coverage:
	$(PYTHON) -m pytest --cov=cdpy
	poetry run coverage-badge -o coverage.svg -f

.PHONY: check
check:
	$(PYTHON) -m mypy .\cdpy\

.PHONY: format
format:
	poetry run black .
	poetry run isort .
