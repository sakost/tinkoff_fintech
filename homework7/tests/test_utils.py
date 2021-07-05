from typing import Union

import pytest

from app.utils import calculate_count_main_pages, escape_path, extend_with_limit


@pytest.mark.parametrize(
    'objs,extend_objs,total_count,returned,result_objs',
    [
        [
            [0, 1, 2],
            [3, 4],
            4,
            ([3], True),
            [0, 1, 2, 3],
        ],
        [
            [0, 1, 2],
            [3, 4],
            3,
            ([], True),
            [0, 1, 2],
        ],
        [
            [0, 1, 2],
            [3, 4],
            2,
            ([], True),
            [0, 1, 2],
        ],
        [
            [0, 1, 2],
            [3, 4],
            5,
            ([3, 4], False),
            [0, 1, 2, 3, 4],
        ],
        [
            [0, 1, 2],
            [3, 4],
            6,
            ([3, 4], False),
            [0, 1, 2, 3, 4],
        ],
    ],
)
def test_extend_with_limit(
    objs: list[int],
    extend_objs: list[int],
    total_count: int,
    returned: tuple[list[int], bool],
    result_objs: list[int],
) -> None:
    assert extend_with_limit(objs, extend_objs, total_count) == returned
    assert objs == result_objs


@pytest.mark.parametrize(
    'articles,result',
    [
        [None, 1],
        [1, 1],
        [25, 1],
        [26, 2],
        [301, 13],
    ],
)
def test_calculate_count_main_pages(articles: Union[None, int], result: int) -> None:
    if articles is None:
        assert calculate_count_main_pages() == result
    else:
        assert calculate_count_main_pages(articles) == result


@pytest.mark.parametrize(
    'path,result',
    [
        ['test/ text', 'test| text'],
        ['test text', 'test text'],
    ],
)
def test_escape_path(path: str, result: str) -> None:
    assert escape_path(path) == result
