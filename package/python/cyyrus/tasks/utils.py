import base64
import difflib
import re
from typing import Any, Dict, List, TypeVar, Union

from cyyrus.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class GeneralUtils:
    @staticmethod
    def extend_or_append(
        lst: List[T],
        item: Union[T, List[T]],
    ) -> List[T]:
        """
        Extends the list if item is a list, or appends item if it's a single element.

        :param lst: The list to be modified
        :param item: The item or list of items to be added
        :return: The modified list
        """
        if isinstance(item, list):
            lst.extend(item)
        else:
            lst.append(item)
        return lst

    @staticmethod
    def flatten_dict(
        d: Dict[str, Any],
        parent_key: str = "",
        sep: str = "_",
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """
        Attempts to flatten the dictionary to a single level, by concatenating the keys with the separator. Upto the specified max_depth.
        """
        logger.debug(f"Attempting to flatten output with max_depth {max_depth} ...")
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and max_depth > 1:
                items.extend(
                    GeneralUtils.flatten_dict(
                        v,
                        new_key,
                        sep,
                        max_depth - 1,
                    ).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def populate_template(
        template: str,
        data: Dict[str, Any],
    ) -> str:
        def get_nested_value(
            keys: List[str],
            nested_data: Dict[str, Any],
        ) -> Any:
            """Recursively get value from nested dictionary."""
            for key in keys:
                if isinstance(nested_data, dict) and key in nested_data:
                    nested_data = nested_data[key]
                else:
                    return None
            return nested_data

        def replace_placeholder(
            match,
        ):
            placeholder = match.group(1).strip()
            keys = placeholder.split(".")
            value = get_nested_value(keys, data)
            return str(value) if value is not None else f"{{{placeholder}}}"

        pattern = r"\{([^}]+)\}"
        return re.sub(pattern, replace_placeholder, template)


class NestedDictAccessor:
    MAX_DEPTH: int = 4

    @staticmethod
    def _find_closest_key(
        keys: List[str],
        target: str,
    ) -> str:
        """
        Find the closest matching key from the list of keys.
        """
        if not keys:
            return ""
        return max(
            keys,
            key=lambda k: difflib.SequenceMatcher(None, k, target).ratio(),
        )

    @staticmethod
    def get_nested_value(
        data: Dict[str, Any],
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a value from a nested dictionary using a dot-separated key string.
        If the exact key is not found, it attempts to find the closest matching key at each level.

        :param data: The input dictionary
        :param key: Dot-separated string representing the nested key
        :param default: Default value to return if key is not found
        :return: The value found or the default
        """

        def _get_value(
            current_data: Dict[str, Any],
            keys: List[str],
            current_depth: int = 0,
        ) -> Any:
            if (
                current_depth >= NestedDictAccessor.MAX_DEPTH
                or not keys
                or not isinstance(current_data, dict)
            ):
                return current_data

            current_key = keys[0]
            if current_key in current_data:
                return _get_value(current_data[current_key], keys[1:], current_depth + 1)
            else:
                logger.debug(f"Key '{current_key}' not found, attempting to find closest match...")
                closest_key = NestedDictAccessor._find_closest_key(
                    list(current_data.keys()),
                    current_key,
                )
                if closest_key:
                    logger.debug(f"Closest key found: '{closest_key}'")
                    return _get_value(
                        current_data[closest_key],
                        keys[1:],
                        current_depth + 1,
                    )
                else:
                    logger.debug(f"No suitable key found for '{current_key}'")
                    return default

        key_parts = key.split(".")
        result = _get_value(data, key_parts)
        return result if result is not None else default


class Base64ImageFinder:
    MAX_DEPTH: int = 5

    @staticmethod
    def is_base64_image(
        value: str,
    ) -> bool:
        """
        Check if a string is a base64 encoded image.
        """
        logger.debug("Checking if string is a base64 encoded image ...")
        try:
            # Attempt to decode the string
            decoded = base64.b64decode(value)
            # Check for common image headers (you might want to expand this list)
            return decoded.startswith(
                (
                    b"\xFF\xD8\xFF",  # JPEG
                    b"\x89PNG\r\n\x1a\n",  # PNG
                    b"GIF87a",  # GIF
                    b"GIF89a",  # GIF
                    b"RIFF",  # WEBP
                )
            )
        except Exception as e:
            logger.debug(f"Error decoding base64: {e}")
            return False

    @staticmethod
    def find_base64_encoded_keys(
        task_input: Dict[str, Any],
    ) -> List[str]:
        """
        Find base64 encoded images inside input up to 5 levels of nesting.
        """
        logger.debug("Attempting to find multimodal keys in task input ...")

        def search_nested(
            data: Dict[str, Any], current_path: str = "", current_depth: int = 0
        ) -> List[str]:
            keys = []
            if current_depth >= Base64ImageFinder.MAX_DEPTH:
                return keys

            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key

                if isinstance(value, str) and Base64ImageFinder.is_base64_image(value):
                    keys.append(new_path)
                elif isinstance(value, dict):
                    keys.extend(search_nested(value, new_path, current_depth + 1))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            keys.extend(search_nested(item, f"{new_path}[{i}]", current_depth + 1))
                        elif isinstance(item, str) and Base64ImageFinder.is_base64_image(item):
                            keys.append(f"{new_path}[{i}]")

            return keys

        return search_nested(task_input)
