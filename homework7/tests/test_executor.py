import concurrent.futures
from unittest import mock

import pytest

from app import executor
from app.data import PageContent


@pytest.mark.parametrize(
    'articles,call_count',
    [
        [25, 1],
        [26, 2],
        [1, 1],
    ],
)
@mock.patch('app.executor.get_articles_links')
def test_submit_execution_main_pages(
    func_mock: mock.Mock,
    articles: int,
    call_count: int,
    dummy_executor: concurrent.futures.Executor,
) -> None:
    func_mock.return_value = func_mock
    for future in executor.submit_execution_main_pages(dummy_executor, articles):
        assert future.result() == func_mock
    assert func_mock.call_count == call_count


@mock.patch('app.executor.parse_article')
def test_submit_execution_articles(
    func_mock: mock.Mock, dummy_executor: concurrent.futures.Executor
):
    func_mock.return_value = func_mock
    futures = executor.submit_execution_articles(
        dummy_executor,
        [
            'https://example.com/link1',
            'https://example.com/link2',
        ],
    )
    assert func_mock.call_count == 2
    assert func_mock.call_args_list == [
        mock.call('https://example.com/link1'),
        mock.call('https://example.com/link2'),
    ]

    for future in futures:
        assert future.result() == func_mock


@pytest.mark.parametrize(
    'articles,links',
    [
        [1, 1],
        [2, 1],
        [3, 4],
    ],
)
@mock.patch('app.executor.submit_execution_articles')
@mock.patch('app.executor.submit_execution_main_pages')
def test_scrape_concurrent(
    main_func_mock: mock.Mock,
    articles_func_mock: mock.Mock,
    dummy_executor: concurrent.futures.Executor,
    articles: int,
    links: int,
):
    future = concurrent.futures.Future()  # type: ignore[var-annotated]
    future.set_result([f'https://example.org/link{link+1}' for link in range(links)])
    main_func_mock.return_value = [future, future]
    future = concurrent.futures.Future()
    result = PageContent('title', 'text', ('image1', 'image2'))
    future.set_result(result)
    articles_func_mock.return_value = {future: 'link'}
    assert list(executor.scrape_concurrent(dummy_executor, articles))[-1] == result
