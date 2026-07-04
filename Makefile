file      := ./src

.PHONY: install-dev install-doc \
	lint format ty test \
	robocop-lint robocop-format docstrfmt sphinxlint \
	doc doc-serve atest

all: lint format ty sphinxlint docstrfmt robocop-lint test robocop-format

install-dev:
	pip install -e ".[dev]"

install-doc:
	pip install -e ".[doc]"

lint:
	ruff check --fix $(file)

format:
	ruff format --check $(file)

ty:
	ty check $(file)

docstrfmt:
	docstrfmt $(file)

sphinxlint:
	sphinx-lint --max-line-length 120 $(file)

test:
	pytest -v --tb=short $(file)

robocop-lint:
	robocop check $(file)

robocop-format:
	robocop format $(file)

doc:
	libdoc robotframework_lynqa.LynqaLibrary::fake_api_key docs/libdoc/LynqaLibrary.html
	zensical build --strict --clean --config-file ./docs/zensical.toml

doc-serve:
	zensical serve --open --config-file ./docs/zensical.toml

atest:
	robot --outputdir results src/robotframework_lynqa/atest
