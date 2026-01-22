# -------------------------
# Configurable variables
# -------------------------

PYTHON      := python
SCRIPT      := generate.py

# Defaults (can be overridden)
START_YEAR  ?= 2022
NUM     ?= 4

# -------------------------
# Targets
# -------------------------

.PHONY: generate help

## Run generator with variables
generate:
	$(PYTHON) $(SCRIPT) $(START_YEAR) $(NUM)

## Show usage
help:
	@echo "Usage:"
	@echo "  make generate START_YEAR=2022 NUM=4"