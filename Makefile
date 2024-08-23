# Makefile

# ==============================================================================
# 										Variables
# ==============================================================================

# Define directory configs
BASE_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR := $(BASE_DIR)/.venv
SRC_DIR := $(BASE_DIR)/package/python
DIST_DIR := $(BASE_DIR)/dist
TEST_DIR := $(BASE_DIR)/tests
REQUIREMENTS_DIR := $(BASE_DIR)/requirements

# Pip tools related configs
PIP_COMPILE := pip-compile
PIP_SYNC := pip-sync
PIP_INSTALL := pip install
PIP := $(VENV_DIR)/bin/pip

# Test related configs
PYTEST_OPTIONS := -vv -n auto

# Detect operating system
ifeq ($(OS),Windows_NT)
    PACKAGE_MANAGER := choco
    PACKAGE_MANAGER_INSTALL := install -y
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        PACKAGE_MANAGER := brew
        PACKAGE_MANAGER_INSTALL := install
    else
        PACKAGE_MANAGER := apt-get
        PACKAGE_MANAGER_INSTALL := install -y
    endif
endif

# Conditional map executable
PYTHON_VERSION := 3.11

ifeq ($(VIRTUAL_ENV),)
    PYTHON := python$(PYTHON_VERSION)
else
    PYTHON := python3
endif

# Define the default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'

## check-prereqs: Check pre-requisites for the project
.PHONY: check-prereqs
check-prereqs:
	@echo "Checking pre-requisites..."
	@which $(PYTHON) > /dev/null 2>&1 || (echo "Python $(PYTHON_VERSION) is not installed. Please install it and try again." && exit 1)
	@$(PYTHON) --version | grep $(PYTHON_VERSION) > /dev/null 2>&1 || (echo "Python $(PYTHON_VERSION) is required. Please install it and try again." && exit 1)
	@which docker > /dev/null 2>&1 || (echo "Docker is not installed. Please install it and try again." && exit 1)
	@echo "All pre-requisites are satisfied."

## init: Initialize the project
.PHONY: init
init: check-prereqs
	@echo "== Initializing Development Environment =="
	@$(PACKAGE_MANAGER) $(PACKAGE_MANAGER_INSTALL) node
	@$(PACKAGE_MANAGER) $(PACKAGE_MANAGER_INSTALL) pre-commit

	@echo "== Installing Pre-Commit Hooks =="
	pre-commit install
	pre-commit autoupdate
	pre-commit install --install-hooks
	pre-commit install --hook-type commit-msg

	@echo "== Constraint Development Environment  =="
	@$(PIP_INSTALL) -r $(REQUIREMENTS_DIR)/pip-requirements.txt
	@$(PIP_INSTALL) --upgrade setuptools wheel build

## dev: Set up the development environment
.PHONY: dev
dev: init update-dependencies

## update-dependencies: Update all dependencies
.PHONY: update-dependencies
update-dependencies: compile-dependencies sync-dependencies

## sync-dependencies: Sync dependencies using pip-sync
.PHONY: sync-dependencies
sync-dependencies:
	@cd $(BASE_DIR) && $(PIP_SYNC) $(REQUIREMENTS_DIR)/requirements-dev.txt

## compile-dependencies: Compile all dependency files
.PHONY: compile-dependencies
compile-dependencies:
	@$(MAKE) compile-requirements
	@$(MAKE) compile-constraints
	@$(MAKE) compile-dev-requirements

## compile-requirements: Compile main requirements file
compile-requirements:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --generate-hashes --no-strip-extras -o $(REQUIREMENTS_DIR)/requirements.txt $(REQUIREMENTS_DIR)/requirements.in

## compile-constraints: Compile constraints file
compile-constraints:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --upgrade --strip-extras -o $(REQUIREMENTS_DIR)/constraints.txt $(REQUIREMENTS_DIR)/requirements.in

## compile-dev-requirements: Compile development requirements file
compile-dev-requirements:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --generate-hashes --no-strip-extras -o $(REQUIREMENTS_DIR)/requirements-dev.txt $(REQUIREMENTS_DIR)/requirements-dev.in

# Define variables for add-dependency target
package ?=
version ?=
dev ?= false
update ?= false

## add-dependency: Add a new dependency to the project (Usage - make add-dependency package=<name> version=<version> [dev=true] [update=true])
.PHONY: add-dependency
add-dependency:
	@if [ -z "$(package)" ]; then \
		echo "Error: Package name is required. Use 'make add-dependency package=<name> version=<version>'"; \
		exit 1; \
	fi
	@req_file=""; \
	if [ "$(dev)" = "true" ]; then \
		echo "Adding to dev requirements"; \
		req_file="$(REQUIREMENTS_DIR)/requirements-dev.in"; \
	else \
		echo "Adding to main requirements"; \
		req_file="$(REQUIREMENTS_DIR)/requirements.in"; \
	fi; \
	if [ ! -f "$$req_file" ]; then \
		echo "Error: Requirements file $$req_file not found."; \
		exit 1; \
	fi; \
	if grep -q "^$(package)==" "$$req_file"; then \
		echo "Package $(package) already exists in $$req_file. Updating version if necessary."; \
		sed -i.bak "s/^$(package)==.*/$(package)==$(version)/" "$$req_file" && rm -f "$$req_file.bak"; \
		if ! grep -q "^$(package)==$(version)$$" "$$req_file"; then \
			echo "Error: Failed to update package version in $$req_file"; \
			exit 1; \
		fi; \
	else \
		echo "Adding $(package)==$(version) to $$req_file"; \
		if [ -s "$$req_file" ] && [ "$$(tail -c 1 < "$$req_file")" != "" ]; then \
			echo >> "$$req_file"; \
		fi; \
		echo "$(package)==$(version)" >> "$$req_file"; \
	fi; \
	if command -v $(PIP_INSTALL) >/dev/null 2>&1; then \
		echo "Installing package with $(PIP_INSTALL)"; \
		$(PIP_INSTALL) $(package)==$(version); \
	else \
		echo "Warning: $(PIP_INSTALL) command not found. Package not installed."; \
	fi; \
	if [ "$(update)" = "true" ]; then \
		echo "Updating dependencies"; \
		$(MAKE) update-dependencies; \
	fi

## build: Build the project
.PHONY: build
build: update-dependencies
	@echo "== Building the project =="
	@$(PYTHON) -m build

## test: Run project tests
.PHONY: test
test:
	@echo "== Triggering tests =="
	pytest $(PYTEST_OPTIONS)

## publish: Publish the project to TestPyPI
.PHONY: publish
publish: test build
	@echo "== Attempting to publish to TestPyPI =="
	twine upload --repository testpypi $(DIST_DIR)/*

## experimental: Create an experimental session with the package
.PHONY: experimental
experimental:
	cd experimental && PYTHONPATH=$(realpath package/python) JUPYTER_PATH=$(realpath .) jupyter-notebook --NotebookApp.token='' --NotebookApp.password=''

## check: Run code quality checks (lint and format)
.PHONY: check
check: lint format

## lint: Run linting checks
.PHONY: lint
lint:
	@echo "== Running Linting =="
	$(VENV_DIR)/bin/ruff check $(SRC_DIR) $(TEST_DIR)

## format: Run code formatting checks
.PHONY: format
format:
	@echo "== Running Formatting =="
	$(VENV_DIR)/bin/black --check $(SRC_DIR) $(TEST_DIR)

## fix: Run code quality checks and fix issues (lint-fix and format-fix)
.PHONY: fix
fix: lint-fix format-fix

## lint-fix: Run linting and fix issues
.PHONY: lint-fix
lint-fix:
	@echo "== Running Linting =="
	$(VENV_DIR)/bin/ruff check --fix $(SRC_DIR) $(TEST_DIR)

## format-fix: Run code formatting and fix issues
.PHONY: format-fix
format-fix:
	@echo "== Running Formatting =="
	$(VENV_DIR)/bin/black $(SRC_DIR) $(TEST_DIR)

## clean: Clean the project (Usage - make clean [dev=true])
.PHONY: clean
clean:
	@echo "== Starting clean process =="
	@if [ "$(dev)" = "true" ]; then \
		echo "== Cleaning development artifacts =="; \
		rm -rf $(VENV_DIR); \
		find . -type d -name '__pycache__' -exec rm -rf {} +; \
		find . -type d -name '.pytest_cache' -exec rm -rf {} +; \
	fi
	@echo "== Cleaning distributable artifacts =="
	@rm -rf $(DIST_DIR)
	@echo "== Clean process completed =="

EXPORT ?= false
DEBUG_FILE := env.debug

## debug: Debug build environment (Usage - make debug [EXPORT=true])
.PHONY: debug
debug:
ifeq ($(EXPORT),true)
	@echo -e "# Environment Information\n\n- *Operating System: $(shell uname -a)\n- **Python Version: $(shell python3 --version)\n- **Installed Packages*:\n\n$(shell pip3 freeze)" > $(DEBUG_FILE)
	@echo "Information exported to $(DEBUG_FILE)"
else
	@echo -e "# Environment Information\n\n- *Operating System: $(shell uname -a)\n- **Python Version: $(shell python3 --version)\n- **Installed Packages*:\n\n$(shell pip3 freeze)"
endif