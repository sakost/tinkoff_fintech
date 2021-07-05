from typing import TypeVar

T = TypeVar('T')

MAX_POSTS_PER_PAGE = 25


def extend_with_limit(
    objs: list[T], extend_objs: list[T], total_count: int
) -> tuple[list[T], bool]:
    """
    :param objs: the list to extend
    :param extend_objs: the list which would extend
    :param total_count: total possible count of objects
    :return: stripped extend_objs
    """
    cur_list_len = len(extend_objs)
    list_len = len(objs)
    difference = total_count - (list_len + cur_list_len)
    exceed = False

    if difference < 0:
        extend_objs = extend_objs[:difference]
        exceed = True

    objs.extend(extend_objs)

    return extend_objs, exceed


def calculate_count_main_pages(articles: int = 1) -> int:
    return articles // MAX_POSTS_PER_PAGE + bool(articles % MAX_POSTS_PER_PAGE)


def escape_path(filepath: str) -> str:
    return filepath.replace('/', '|')
