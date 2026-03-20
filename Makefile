PYTHON     = venv/bin/python
PIP        = venv/bin/pip
REGIONE   ?= Umbria
N         ?= 10

.PHONY: setup install db-start db-stop frazioni run

setup: install
	venv/bin/playwright install chromium

install:
	python3 -m venv venv
	$(PIP) install -r requirements.txt

db-start:
	docker compose up -d

db-stop:
	docker compose down

frazioni:
	$(PYTHON) pipeline/frazioni.py $(REGIONE)

run:
	$(PYTHON) pipeline/main.py --regione $(REGIONE) --n $(N)
