from typing import List, TypeVar, Union

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
