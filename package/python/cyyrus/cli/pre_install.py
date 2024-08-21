# pre_install.py

import platform
import subprocess
import sys


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        result.check_returncode()
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip())


def install_package(command, package_name):
    try:
        output = run_command(command)
        print(output)
        return output
    except RuntimeError as e:
        raise RuntimeError(f"Failed to install {package_name}: {e}")


def check_and_install():
    try:
        # Check and install Poppler
        try:
            run_command("pdftoppm -h")
        except RuntimeError:
            if platform.system() == "Darwin":  # macOS
                install_package("brew install poppler", "Poppler")
            elif platform.system() == "Linux":  # Linux
                install_package(
                    "sudo apt-get update && sudo apt-get install -y poppler-utils",
                    "Poppler",
                )
            else:
                raise RuntimeError(
                    "Please install Poppler manually from https://poppler.freedesktop.org/"
                )

        # Check and install FFmpeg
        try:
            run_command("ffmpeg -version")
            print("FFmpeg is already installed.")
        except RuntimeError:
            if platform.system() == "Darwin":  # macOS
                install_package("brew install ffmpeg", "FFmpeg")
            elif platform.system() == "Linux":  # Linux
                install_package(
                    "sudo apt-get update && sudo apt-get install -y ffmpeg",
                    "FFmpeg",
                )
            else:
                raise RuntimeError(
                    "Please install FFmpeg manually from https://ffmpeg.org/download.html"
                )

    except RuntimeError as err:
        print(f"Error during installation: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    check_and_install()
