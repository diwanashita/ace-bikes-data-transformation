# -------------------------
# Configurable variables
# -------------------------

PYTHON      := python

# Defaults (can be overridden)
START_YEAR  ?= 2022
NUM     ?= 4

# -------------------------
# Targets
# -------------------------

.PHONY: generate help

## Run generator with variables
generate:
	rm -rf ./data_new
	rm -rf ./data_full

	mkdir ./data_new
	mkdir ./data_full
	
	$(PYTHON) ./src/generate_customer_employee_order.py $(START_YEAR) $(NUM)
	$(PYTHON) ./src/generate_line_item_sales.py
	$(PYTHON) ./src/generate_inventory.py
	$(PYTHON) ./src/update_ace_bikes_data.py
	$(PYTHON) ./src/concatenate.py
	$(PYTHON) ./src/copy_existing.py
	$(PYTHON) ./src/generate_reviews.py $(START_YEAR) $(NUM)
	$(PYTHON) ./src/generate_webstats.py $(START_YEAR) $(NUM)


install:
	pip install -r requirements.txt

## Show usage
help:
	@echo "Usage:"
	@echo "  make generate START_YEAR=2022 NUM=4"