install:
	python -m pip install -r requirements.txt

run:
	python -m src.pipeline

query:
	python -m src.analytics

.PHONY: test pipeline check

test:
	python -m pytest -v

pipeline:
	python -m src.pipeline

check: test