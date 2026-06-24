VENV        := .venv/bin
file      := .

.PHONY: lint format ty test robocop-lint robocop-format

lint:
	$(VENV)/ruff check --fix $(file)

format:
	$(VENV)/ruff format $(file)

ty:
	$(VENV)/ty check $(file)

test:
	$(VENV)/pytest -v --tb=short $(file)

robocop-lint:
	$(VENV)/robocop check $(file)

robocop-format:
	$(VENV)/robocop format $(file)
