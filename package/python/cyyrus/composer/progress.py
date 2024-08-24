from typing import Any, Iterable, Optional, TypeVar

T = TypeVar("T")


def conditional_tqdm(
    iterable: Iterable[T],
    use_tqdm: bool = True,
    desc: Optional[str] = None,
    total: Optional[int] = None,
    **kwargs: Any,
):
    """
    A wrapper around tqdm that allows conditional use of the progress bar.

    Args:
        iterable (Iterable[T]): The iterable to wrap with tqdm.
        use_tqdm (bool): Whether to use tqdm or not. Defaults to True.
        desc (str, optional): Description to use for the progress bar.
        total (int, optional): The total number of iterations. If None, len(iterable) is used if possible.
        **kwargs: Additional keyword arguments to pass to tqdm.

    Returns:
        Iterator[T]: The wrapped iterable, either with tqdm progress bar or the original iterable.

    Example:
        ```python
        for item in tqdm_wrapper(items, use_tqdm=True, desc="Processing"):
            process(item)
        ```
    """
    if use_tqdm:
        from tqdm import tqdm

        return tqdm(iterable, desc=desc, total=total, **kwargs)
    else:
        return iter(iterable)
