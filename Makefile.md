# Makefile README

This README provides an overview of the various commands available in the project's Makefile for dependency management, building the project, running tests, maintaining code quality, and cleaning up artifacts amongst others.

```
Usage: make [target]

Targets:
 check-prereqs               Check pre-requisites for the project
 init                        Initialize the project
 dev                         Set up the development environment
 update-dependencies         Update all dependencies
 sync-dependencies           Sync dependencies using pip-sync
 compile-dependencies        Compile all dependency files
 compile-requirements        Compile main requirements file
 compile-constraints         Compile constraints file
 compile-dev-requirements    Compile development requirements file
 add-dependency              Add a new dependency to the project (Usage: make add-dependency package=<name> version=<version> [dev=true] [update=true])
 build                       Build the project
 test                        Run project tests
 publish                     Publish the project to TestPyPI
 experimental                Create an experimental session with the package
 check                       Run code quality checks (lint and format)
 lint                        Run linting checks
 format                      Run code formatting checks
 fix                         Run code quality checks and fix issues (lint-fix and format-fix)
 lint-fix                    Run linting and fix issues
 format-fix                  Run code formatting and fix issues
 clean                       Clean the project (Usage: make clean [dev=true])
 debug                       Debug build environment (Usage: make debug [EXPORT=true])
 ```

## Table of Contents

1. [Initialization](#initialization)
2. [Dependency Management](#dependency-management)
3. [Build and Test](#build-and-test)
4. [Code Quality with Fix](#code-quality-with-fix)
5. [Clean Up](#clean-up)
6. [Usage](#usage)
7. [Variables](#variables)

## Initialization

### `init`
Initializes the development environment by installing necessary tools and pre-commit hooks.

```sh
make init
```

**Steps:**
1. Installs `node` and `pre-commit` using the system package manager.
2. Sets up pre-commit hooks.

## Dependency Management

### `update-dependencies`
Updates dependencies and optionally synchronizes them.

```sh
make update-dependencies [sync=true]
```

**Parameters:**
- `sync` (default: `false`): If `true`, syncs dependencies after updating.

### `sync-dependencies`
Synchronizes dependencies with `requirements.txt` and `requirements-dev.txt`.

```sh
make sync-dependencies
```

### `compile-dependencies`
Compiles all dependency files into `requirements.txt`, `constraints.txt`, and `requirements-dev.txt`.

```sh
make compile-dependencies
```


### `add-dependency`
Adds a new dependency to the project.

```sh
make add-dependency package=<package> version=<version> [dev=false] [update=false]
```

**Parameters:**
- `package`: The name of the package to add.
- `version`: The version of the package.
- `dev` (default: `false`): If `true`, adds the dependency to `requirements-dev.in`.
- `update` (default: `false`): If `true`, updates dependencies after adding.

## Build and Test

### `build`
Builds the project and updates dependencies.

```sh
make build
```

**Steps:**
1. Updates dependencies.
2. Builds the project using `python -m build`.

### `test`
Runs tests in the `tests` directory using `pytest`.

```sh
make test
```

### `debug`
Assists in inspecting the current environment.

```sh
make debug
```

**Parameters:**
- `EXPORT` boolean flag whether to trigger debug dump
- `DEBUG_FILE` defines the debug file for exporting dumps

## Code Quality with Fix

### `check`
Checks code quality by running linting and formatting checks.

```sh
make check
```

**Steps:**
1. Updates dependencies.
2. Runs linting with `ruff`.
3. Checks code formatting with `black`.

### `lint`
Runs linting checks.

```sh
make lint
```

### `format`
Checks code formatting.

```sh
make format
```

### `fix`
Automatically fixes code quality issues by applying linting and formatting fixes.

```sh
make fix
```

**Steps:**
1. Updates dependencies.
2. Runs linting fixes.
3. Applies formatting fixes.

## Clean Up

### `clean`
Cleans up build artifacts and development environment.

```sh
make clean [dev=false]
```

**Parameters:**
- `dev` (default: `false`): If `true`, removes development artifacts like the virtual environment and cache directories.

**Steps:**
1. If `dev` is `true`, removes development artifacts and caches.
2. Removes distributable artifacts from the `dist` directory.

## Usage

To use the `Makefile`, navigate to the project directory and run `make` followed by the desired target. For example:

```sh
make build
```

## Variables

### Variables Configured in the Makefile
- **`BASE_DIR`**: The base directory of the project.
- **`VENV_DIR`**: Directory for the virtual environment.
- **`SRC_DIR`**: Source code directory.
- **`DIST_DIR`**: Distribution directory.
- **`TEST_DIR`**: Test directory.
- **`PIP_COMPILE`**: Command for compiling dependencies.
- **`PIP_SYNC`**: Command for syncing dependencies.
- **`PIP_INSTALL`**: Command for installing packages.
- **`PIP`**: Path to the pip executable in the virtual environment.
- **`PYTEST_OPTIONS`**: Options for running pytest.
- **`PACKAGE_MANAGER`**: System package manager (e.g., `apt-get`, `brew`, `choco`).
- **`PYTHON_VERSION`**: Python version used.
