# Top-level convenience targets. The real Gazebo/ROS2 launch lives in sim/.

PY ?= python

install:
	$(PY) -m pip install -e .[dev,agent]

lint:
	$(PY) -m ruff check src tests

test:
	$(PY) -m pytest

demo: ## Run the full headless demo and write site/demo-trace.json
	$(PY) -m scripts.record_trace --out site/demo-trace.json

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache **/__pycache__

.PHONY: install lint test demo clean
