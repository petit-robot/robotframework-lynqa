RUFF_CONFIG := cfg/python/ruff.toml
VENV        := .venv/bin
file      := .

.PHONY: lint format

lint:
	$(VENV)/ruff check --config $(RUFF_CONFIG) $(file)

format:
	$(VENV)/ruff format --config $(RUFF_CONFIG) $(file)
