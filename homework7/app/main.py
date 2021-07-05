import concurrent.futures

from .executor import scrape_concurrent
from .exporter import export_content


def main(articles: int = 1, threads: int = 1) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for content in scrape_concurrent(executor, articles):
            futures.extend(export_content(executor, content))

        for future in concurrent.futures.as_completed(futures):
            future.result()
