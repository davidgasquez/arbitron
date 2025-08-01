.PHONY: .uv
.uv:
	@uv --version || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: setup
setup: .uv
	uv sync --frozen

build:
	uv build

publish: build
	uv publish

lint:
	uvx ruff check
	uvx ty check
