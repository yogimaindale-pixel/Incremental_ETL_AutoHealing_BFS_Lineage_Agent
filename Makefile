.PHONY: setup test demo clean reset api

setup:
	bash scripts/bootstrap.sh

seed:
	python3 scripts/seed_demo_data.py

test:
	bash scripts/run_tests.sh

demo:
	python3 run_demo.py --all-scenarios

reset:
	python3 scripts/reset_demo.py

api:
	uvicorn src.api.app:app --reload --port 8000
