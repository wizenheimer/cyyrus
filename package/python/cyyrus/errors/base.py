from typing import Any, Optional, Dict


class CyyrusException(Exception):

    def __init__(
        self,
        message: Optional[str] = None,
        extra_info: Optional[Dict[Any, Any]] = None,
    ):
        self.message = message
        self.extra_info = extra_info
        super().__init__(self.message)

    def __str__(self):
        if self.extra_info:
            return f"{self.message} (Extra Info: {self.extra_info})"
        return self.message


class CyyrusWarning(Warning):

    def __init__(
        self,
        message: Optional[str] = None,
        extra_info: Optional[Dict[Any, Any]] = None,
    ):
        self.message = message
        self.extra_info = extra_info
        super().__init__(self.message)

    def __str__(self):
        if self.extra_info:
            return f"{self.message} (Extra Info: {self.extra_info})"
        return self.message
