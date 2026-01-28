# -------------------------
# Configurable variables
# -------------------------

PYTHON      := python
SCRIPT      := generate_customer_employee_order.py

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
	$(PYTHON) generate_line_item_sales.py
	$(PYTHON) generate_inventory.py
	$(PYTHON) concatenate.py

install:
	pip install -r requirements.txt

## Show usage
help:
	@echo "Usage:"
	@echo "  make generate START_YEAR=2022 NUM=4"