import os
import subprocess
import sys
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


class InstallSystemDependencies(install):
    """Post-installation for installation mode."""

    def run(self):
        """Run post-install hook."""
        try:
            subprocess.check_call([sys.executable, "-m", "package.python.extras.pre_install"])
        except subprocess.CalledProcessError as e:
            print(f"Pre-install script failed: {e}", file=sys.stderr)
            sys.exit(1)
        install.run(self)


class InstallDevelopmentSystemDependencies(develop):
    """Post-installation for development mode."""

    def run(self):
        """Run post-install hook."""
        try:
            subprocess.check_call([sys.executable, "-m", "package.python.extras.pre_install"])
        except subprocess.CalledProcessError as e:
            print(f"Pre-install script failed: {e}", file=sys.stderr)
            sys.exit(1)
        install.run(self)  # type: ignore


def parse_requirements(filename):
    with open(filename, "r") as f:
        return [
            line.split("--hash=")[0].strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


requirements_path = os.path.join("requirements", "requirements.in")
requirements = parse_requirements(requirements_path)

packages = find_packages(
    where="package/python",
    exclude=[
        # Exclude tests if present
        "*.tests",
        "*.tests.*",
        "tests.*",
        "tests",
        # Exclude __pycache__ directories
        "*.__pycache__",
        "*.__pycache__.*",
    ],
)

setup(
    name="cyyrus",
    description="...",
    use_scm_version=True,
    author="wizenheimer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="cyyruslabs@gmail.com",
    url="https://github.com/wizenheimer/cyyrus",
    packages=packages,
    package_dir={
        "": "package/python",
    },
    install_requires=requirements,
    cmdclass={
        "install": InstallSystemDependencies,
        "develop": InstallDevelopmentSystemDependencies,
    },
    entry_points={
        "console_scripts": [
            "cyyrus=cyyrus.cli.main:cli",
        ],
    },
    include_package_data=True,
    exclude_package_data={
        "": [".DS_Store"],
        "package": [".DS_Store"],
        "package/python": [".DS_Store"],
        "package/python/cyyrus": [".DS_Store"],
    },
)
