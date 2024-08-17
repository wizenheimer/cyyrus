import sys
from pathlib import Path


def add_package_to_path():
    # Get the absolute path of the project root
    project_root = Path(__file__).parent.resolve()

    # Construct the path to the package
    package_path = project_root / "package" / "python"

    # Convert to absolute path and resolve any symlinks
    package_path = package_path.resolve()

    # Check if the package path exists
    if not package_path.is_dir():
        print(f"Warning: Package directory not found at {package_path}")
        return

    # Convert to string for compatibility with sys.path
    package_path_str = str(package_path)

    # Check if the package path is already in sys.path
    if package_path_str not in sys.path:
        print(f"Adding {package_path_str} to Python path")
        sys.path.insert(0, package_path_str)
    else:
        print(f"{package_path_str} is already in Python path")


# Call the function to add the package to the path
add_package_to_path()
