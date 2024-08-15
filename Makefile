# Makefile

# ==============================================================================
# 										Variables
# ==============================================================================

# Define directory configs
BASE_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_DIR := $(BASE_DIR)/.venv
SRC_DIR := $(BASE_DIR)/src
DIST_DIR := $(BASE_DIR)/dist
TEST_DIR := $(BASE_DIR)/tests

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

# ==============================================================================
# 									Check Pre-requisites
# ==============================================================================
.PHONY: check-prereqs
check-prereqs:
	@echo "Checking pre-requisites..."
	@which $(PYTHON) > /dev/null 2>&1 || (echo "Python $(PYTHON_VERSION) is not installed. Please install it and try again." && exit 1)
	@$(PYTHON) --version | grep $(PYTHON_VERSION) > /dev/null 2>&1 || (echo "Python $(PYTHON_VERSION) is required. Please install it and try again." && exit 1)
	@which docker > /dev/null 2>&1 || (echo "Docker is not installed. Please install it and try again." && exit 1)
	@echo "All pre-requisites are satisfied."

# ==============================================================================
# 									Initialization
# ==============================================================================

# Target to initialize the development environment
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
	@$(PIP_INSTALL) -r pip-requirements.txt
	@$(PIP_INSTALL) --upgrade setuptools wheel build

# Target to setup the development environment
.PHONY: dev
dev: init update-dependencies

# ==============================================================================
# 							Dependency Management
# ==============================================================================

# Target to update dependencies from requirements.txt and requirements-dev.txt files into virtual environment
.PHONY: update-dependencies
update-dependencies: compile-dependencies sync-dependencies

# Target to sync dependencies from requirements.txt and requirements-dev.txt files into virtual environment
.PHONY: sync-dependencies
sync-dependencies:
	@cd $(BASE_DIR) && $(PIP_SYNC) requirements-dev.txt

# Target to compile dependencies from requirements.in and requirements-dev.in files into requirements.txt and requirements-dev.txt
.PHONY: compile-dependencies
compile-dependencies:
	@$(MAKE) compile-requirements
	@$(MAKE) compile-constraints
	@$(MAKE) compile-dev-requirements

compile-requirements:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --generate-hashes --no-strip-extras requirements.in

compile-constraints:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --upgrade --strip-extras -o constraints.txt requirements.in

compile-dev-requirements:
	@cd $(BASE_DIR) && $(PIP_COMPILE) -q --allow-unsafe --resolver=backtracking --generate-hashes --no-strip-extras requirements-dev.in

# Define variables for add-dependency target
package ?=
version ?=
dev ?= false
update ?= false

# Target to add dependencies
.PHONY: add-dependency
add-dependency:
	@if [ -z "$(package)" ]; then \
		echo "Error: Package name is required. Use 'make add-dependency package=<name> version=<version>'"; \
		exit 1; \
	fi
	@req_file=""; \
	if [ "$(dev)" = "true" ]; then \
		echo "Adding to dev requirements"; \
		req_file="$(BASE_DIR)/requirements-dev.in"; \
	else \
		echo "Adding to main requirements"; \
		req_file="$(BASE_DIR)/requirements.in"; \
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


# ==============================================================================
# 								Build and Test
# ==============================================================================
# Targets to Build the project
.PHONY: build
build: update-dependencies
	@echo "== Building the project =="
	@$(PYTHON) -m build

# Targets to Test out the build
.PHONY: test
test: update-dependencies
	@echo "== Triggering tests =="
	pytest $(TEST_DIR)/* $(PYTEST_OPTIONS)

# Targets to Publish the project to TestPyPI
.PHONY: publish
publish: test build
	@echo "== Attempting to publish to TestPyPI =="
	twine upload --repository testpypi $(DIST_DIR)/*

# Target to create an experimental session with package
.PHONY: experimental
experimental:
	cd experimental && PYTHONPATH=$(realpath src) JUPYTER_PATH=$(realpath .) jupyter-notebook --NotebookApp.token='' --NotebookApp.password=''

# ==============================================================================
# 								Code Quality with Fix
# ==============================================================================

# Targets for Code Quality
.PHONY: check
check: update-dependencies lint format

.PHONY: lint
lint:
	@echo "== Running Linting =="
	$(VENV_DIR)/bin/ruff check $(SRC_DIR) $(TEST_DIR)

.PHONY: format
format:
	@echo "== Running Formatting =="
	$(VENV_DIR)/bin/black --check $(SRC_DIR) $(TEST_DIR)

# Targets for Code Quality with Fix
.PHONY: fix
fix: update-dependencies lint-fix format-fix

.PHONY: lint-fix
lint-fix:
	@echo "== Running Linting =="
	$(VENV_DIR)/bin/ruff check --fix $(SRC_DIR) $(TEST_DIR)

.PHONY: format-fix
format-fix:
	@echo "== Running Formatmting =="
	$(VENV_DIR)/bin/black $(SRC_DIR) $(TEST_DIR)


# ================================================================================
# 								Clean Up
# =================================================================================

# Clean build artifacts
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