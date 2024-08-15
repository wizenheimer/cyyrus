from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess
import sys


class InstallSystemDependencies(install):
    """Post-installation for installation mode."""

    def run(self):
        """Run post-install hook."""
        try:
            subprocess.check_call([sys.executable, "-m", "src.cyyrus.cli.pre_install"])
        except subprocess.CalledProcessError as e:
            print(f"Pre-install script failed: {e}", file=sys.stderr)
            sys.exit(1)
        install.run(self)


class InstallDevelopmentSystemDependencies(develop):
    """Post-installation for development mode."""

    def run(self):
        """Run post-install hook."""
        try:
            subprocess.check_call([sys.executable, "-m", "src.cyyrus.cli.pre_install"])
        except subprocess.CalledProcessError as e:
            print(f"Pre-install script failed: {e}", file=sys.stderr)
            sys.exit(1)
        install.run(self)


def parse_requirements(filename):
    with open(filename, "r") as f:
        return [
            line.split("--hash=")[0].strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


requirements = parse_requirements("requirements.txt")

setup(
    name="cyyrus",
    description="...",
    use_scm_version=True,
    author="wizenheimer",
    author_email="cyyruslabs@gmail.com",
    url="https://github.com/wizenheimer/cyyrus",
    packages=find_packages("src"),
    package_dir={
        "": "src",
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
)
