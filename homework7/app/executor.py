import concurrent.futures
from typing import Iterator

from .data import PageContent
from .parser import get_articles_links, parse_article
from .utils import calculate_count_main_pages, extend_with_limit


def submit_execution_main_pages(
    executor: concurrent.futures.Executor, articles: int
) -> list[concurrent.futures.Future[list[str]]]:
    futures = [
        executor.submit(get_articles_links, page)
        for page in range(calculate_count_main_pages(articles))
    ]
    return futures


def submit_execution_articles(
    executor: concurrent.futures.Executor, links: list[str]
) -> dict[concurrent.futures.Future[PageContent], str]:
    futures = {executor.submit(parse_article, link): link for link in links}
    return futures


def scrape_concurrent(
    executor: concurrent.futures.Executor, articles: int = 1
) -> Iterator[PageContent]:
    main_pages_futures: list[
        concurrent.futures.Future[list[str]]
    ] = submit_execution_main_pages(executor, articles)
    parse_articles_futures: dict[concurrent.futures.Future[PageContent], str] = {}
    links: list[str] = []
    done = False

    for main_pages_future in main_pages_futures:
        if not done:
            cur_links = main_pages_future.result()
            cur_links, done = extend_with_limit(links, cur_links, articles)
            parse_articles_futures |= submit_execution_articles(executor, cur_links)
        else:
            main_pages_future.cancel()

    for parse_articles_future in concurrent.futures.as_completed(
        parse_articles_futures
    ):
        yield parse_articles_future.result()
