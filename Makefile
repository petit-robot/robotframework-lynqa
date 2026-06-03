RUFF_CONFIG := cfg/python/ruff.toml
TY_CONFIG   := cfg/python/ty.toml
VENV        := .venv/bin
file      := .

.PHONY: lint format ty

lint:
	$(VENV)/ruff check --config $(RUFF_CONFIG) $(file)

format:
	$(VENV)/ruff format --config $(RUFF_CONFIG) $(file)

ty:
	$(VENV)/ty check --config-file $(TY_CONFIG) $(file)
