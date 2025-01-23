#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Docker variables
IMAGE := sparrow-mlpipes
VERSION := latest

.PHONY: test
test:
	pytest --cov=sparrow_mlpipes sparrow_mlpipes/

.PHONY: check-codestyle
check-codestyle:
	isort --diff --check-only sparrow_mlpipes
	black --diff --check sparrow_mlpipes
	pylint sparrow_mlpipes

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		--no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

.PHONY: branchify
branchify:
ifneq ($(shell git rev-parse --abbrev-ref HEAD),main)
	sed -i "s/^version\s*=\s*[0-9]*\.[0-9]*\.[0-9]*/&.dev$(shell date +%s)/g" setup.cfg
endif

.PHONY: publish
publish: branchify
	pip install twine build
	rm -rf dist
	python -m build
	twine upload dist/* --username $(PYPI_USERNAME) --password $(PYPI_PASSWORD)
	git checkout -- setup.cfg
	rm -rf dist

.PHONY: freeze
freeze:
	uv pip compile -q -o requirements.txt setup.cfg
	echo "-e ." >> requirements.txt
	uv pip compile -q --extra dev -o requirements-dev.txt setup.cfg
	echo "-e ." >> requirements-dev.txt
