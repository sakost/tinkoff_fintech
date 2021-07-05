from typing import Any, Callable, Optional


def paginate_query(query: Any, page: int, objects_per_page: int) -> Any:
    return query.limit(objects_per_page).offset(objects_per_page * max(page - 1, 0))


def singleton_cache(func: Callable[..., Any]) -> Callable[..., Any]:
    cached_result: Optional[Any] = None

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal cached_result
        if cached_result is None:
            cached_result = func(*args, **kwargs)
        return cached_result

    return wrapper
